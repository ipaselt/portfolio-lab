"""Charts — price/SMA/RSI + relative strength vs SPY."""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.research.technicals import fetch_history, relative_strength, rsi, sma
from src.ui import AMBER, BLUE, BORDER, GREEN, MUTED, RED, VIOLET, page_header
from src.watchlist import load_watchlist

page_header("Charts", "Daily bars via Yahoo Finance · benchmark SPY · 15-minute cache")

BENCHMARK = "SPY"
PERIODS = {"3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y", "5Y": "5y"}


@st.cache_data(ttl=900, show_spinner=False)
def _history(ticker, period):
    return fetch_history(ticker, period=period)


@st.cache_data(ttl=900, show_spinner=False)
def _holding_symbols():
    """Equity + ETF symbols currently held, via Schwab; empty if auth is stale so the
    page still works with typed/watchlist tickers."""
    try:
        from src.schwab_client import get_accounts_summary, get_client
        accounts = get_accounts_summary(get_client())
        # EQUITY = stocks; COLLECTIVE_INVESTMENT = ETFs (verified live 2026-07-08: SPY/SCHK).
        return sorted({
            p["instrument"]["symbol"]
            for a in accounts for p in a["positions"]
            if p.get("instrument", {}).get("assetType") in ("EQUITY", "COLLECTIVE_INVESTMENT")
        })
    except Exception:
        return []


holdings = _holding_symbols()
watchlist = load_watchlist()
known = sorted(set(holdings) | set(watchlist))

col_pick, col_type, col_period = st.columns([2, 2, 1])
picked = col_pick.selectbox(
    "Holdings + watchlist", [""] + known,
    format_func=lambda t: t or "Select symbol")
typed = col_type.text_input("Any other ticker", placeholder="e.g. TSM").strip().upper()
period_label = col_period.selectbox("Period", list(PERIODS), index=2)

ticker = typed or picked
if not ticker:
    st.info("Pick a ticker from your holdings/watchlist or type one.")
    st.stop()

try:
    with st.spinner(f"Loading {ticker}…"):
        hist = _history(ticker, PERIODS[period_label])
        bench = _history(BENCHMARK, PERIODS[period_label])
except ValueError as e:
    st.warning(str(e))
    st.stop()

close = hist["Close"]

# --- Summary strip ---------------------------------------------------------------
latest = close.iloc[-1]
chg = latest - close.iloc[-2] if len(close) > 1 else 0.0
chg_pct = chg / close.iloc[-2] * 100 if len(close) > 1 and close.iloc[-2] else 0.0
latest_rsi = rsi(close).iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Last close", f"${latest:,.2f}", delta=f"{chg:+,.2f} ({chg_pct:+.2f}%)")
c2.metric("Period high", f"${hist['High'].max():,.2f}")
c3.metric("Period low", f"${hist['Low'].min():,.2f}")
c4.metric("RSI (14)", f"{latest_rsi:.0f}")

# --- Price + SMAs with RSI subplot --------------------------------------------------
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28],
                    vertical_spacing=0.05)
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=close,
    name=ticker, showlegend=False,
    increasing=dict(line=dict(color=GREEN, width=1), fillcolor=GREEN),
    decreasing=dict(line=dict(color=RED, width=1), fillcolor=RED)), row=1, col=1)
for window, color in [(50, AMBER), (200, VIOLET)]:
    if len(close) >= window:
        fig.add_trace(go.Scatter(x=hist.index, y=sma(close, window), name=f"SMA {window}",
                                 line=dict(width=1.4, color=color)), row=1, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=rsi(close), name="RSI 14",
                         line=dict(width=1.3, color=BLUE), showlegend=False), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color=BORDER, line_width=1.4, row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color=BORDER, line_width=1.4, row=2, col=1)
fig.update_layout(
    title=f"{ticker} · {period_label}", height=600, xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))
fig.update_yaxes(title_text=None, tickprefix="$", row=1, col=1)
fig.update_yaxes(title_text="RSI", range=[0, 100], tickvals=[30, 50, 70], row=2, col=1)
st.plotly_chart(fig, use_container_width=True)

# --- Relative strength vs benchmark ---------------------------------------------------
if ticker != BENCHMARK:
    rs_series = relative_strength(close, bench["Close"])
    rs_fig = go.Figure(go.Scatter(x=rs_series.index, y=rs_series, name=f"{ticker} / {BENCHMARK}",
                                  line=dict(color=BLUE, width=1.6)))
    rs_fig.add_hline(y=1.0, line_dash="dot", line_color=MUTED, line_width=1.2)
    rs_fig.update_layout(
        title=f"RELATIVE STRENGTH VS {BENCHMARK} · REBASED — ABOVE 1.0 = OUTPERFORMING",
        height=280, showlegend=False)
    st.plotly_chart(rs_fig, use_container_width=True)

above_50 = len(close) >= 50 and latest > sma(close, 50).iloc[-1]
above_200 = len(close) >= 200 and latest > sma(close, 200).iloc[-1]
st.caption(
    f"Price {'above' if above_50 else 'below'} SMA-50"
    + (f" · {'above' if above_200 else 'below'} SMA-200" if len(close) >= 200 else "")
    + " · data: Yahoo Finance, daily, adjusted")
