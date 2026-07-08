"""Charts page — price/SMA/RSI + relative strength vs SPY for holdings and watchlist tickers."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.research.technicals import fetch_history, relative_strength, rsi, sma
from src.watchlist import load_watchlist

st.set_page_config(page_title="Charts — Portfolio Lab", layout="wide")
st.title("Charts")

BENCHMARK = "SPY"
PERIODS = {"3 months": "3mo", "6 months": "6mo", "1 year": "1y", "2 years": "2y", "5 years": "5y"}


@st.cache_data(ttl=900, show_spinner=False)
def _history(ticker, period):
    return fetch_history(ticker, period=period)


@st.cache_data(ttl=900, show_spinner=False)
def _holding_symbols():
    """Equity symbols currently held, via Schwab. Empty list if auth is stale — the page
    still works with typed/watchlist tickers rather than erroring out."""
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
    "Ticker (holdings + watchlist)", [""] + known,
    format_func=lambda t: t or "(choose)")
typed = col_type.text_input("…or any other ticker", placeholder="e.g. TSM").strip().upper()
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

# --- Price + SMAs with RSI subplot -------------------------------------------
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28],
                    vertical_spacing=0.04)
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=close,
    name=ticker, showlegend=False), row=1, col=1)
for window, color in [(50, "#ff7f0e"), (200, "#9467bd")]:
    if len(close) >= window:
        fig.add_trace(go.Scatter(x=hist.index, y=sma(close, window), name=f"SMA {window}",
                                 line=dict(width=1.5, color=color)), row=1, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=rsi(close), name="RSI 14",
                         line=dict(width=1.2, color="#1f77b4"), showlegend=False), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="gray", row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="gray", row=2, col=1)
fig.update_layout(title=f"{ticker} — {period_label}", height=620,
                  xaxis_rangeslider_visible=False)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
st.plotly_chart(fig, use_container_width=True)

# --- Relative strength vs benchmark -------------------------------------------
if ticker != BENCHMARK:
    rs_series = relative_strength(close, bench["Close"])
    rs_fig = go.Figure(go.Scatter(x=rs_series.index, y=rs_series, name=f"{ticker} vs {BENCHMARK}",
                                  line=dict(color="#2ca02c")))
    rs_fig.add_hline(y=1.0, line_dash="dot", line_color="gray")
    rs_fig.update_layout(
        title=f"Relative strength vs {BENCHMARK} (rebased; >1 = outperforming since window start)",
        height=300)
    st.plotly_chart(rs_fig, use_container_width=True)

latest_rsi = rsi(close).iloc[-1]
above_50 = len(close) >= 50 and close.iloc[-1] > sma(close, 50).iloc[-1]
above_200 = len(close) >= 200 and close.iloc[-1] > sma(close, 200).iloc[-1]
st.caption(
    f"RSI(14): **{latest_rsi:.0f}** · "
    f"price {'above' if above_50 else 'below'} SMA-50"
    + (f" · {'above' if above_200 else 'below'} SMA-200" if len(close) >= 200 else "")
)
