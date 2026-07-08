"""Research — fundamentals snapshot, peer comparison, watchlist."""
import pandas as pd
import streamlit as st

from src.research.fundamentals import comparison_table, fetch_snapshot, format_value
from src.ui import page_header
from src.watchlist import add_ticker, load_watchlist, remove_ticker

# Two-panel split of the snapshot metrics: valuation/price vs profitability/growth.
VALUATION_LABELS = [
    "Price", "Market cap", "P/E (ttm)", "P/E (fwd)", "P/B", "EV/EBITDA", "EPS (ttm)",
    "52w low", "52w high", "Analyst target (mean)", "Analyst consensus",
]
QUALITY_LABELS = [
    "Gross margin", "Op margin", "Net margin", "Revenue growth (yoy)",
    "Earnings growth (yoy)", "ROE", "Debt/Equity", "Free cash flow", "Dividend yield",
]


def _metric_table(metrics, labels):
    rows = [{"Metric": lbl, "Value": format_value(lbl, metrics.get(lbl))} for lbl in labels]
    return pd.DataFrame(rows)

page_header("Research", "Fundamentals via Yahoo Finance · 15-minute cache")


@st.cache_data(ttl=900, show_spinner=False)
def _snapshot(ticker):
    return fetch_snapshot(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def _comparison(tickers):
    return comparison_table(list(tickers))


# --- Single-ticker snapshot ------------------------------------------------------
st.markdown("## Ticker Snapshot")
col_in, col_btn = st.columns([4, 1])
ticker = col_in.text_input("Ticker", placeholder="Enter symbol — e.g. MSFT",
                           label_visibility="collapsed").strip()
add_clicked = col_btn.button("Add to watchlist", disabled=not ticker, use_container_width=True)

if add_clicked and ticker:
    add_ticker(ticker)
    st.toast(f"{ticker.upper()} added to watchlist")

if ticker:
    try:
        with st.spinner(f"Fetching {ticker.upper()}…"):
            snap = _snapshot(ticker.upper())
        st.markdown(f"### {snap['name']}")
        st.caption(f"{snap['sector']} · {snap['industry']}")
        col_val, col_qual = st.columns(2)
        col_val.dataframe(
            _metric_table(snap["metrics"], VALUATION_LABELS),
            use_container_width=True, hide_index=True,
            column_config={"Metric": st.column_config.TextColumn("Valuation & Price"),
                           "Value": st.column_config.TextColumn("", width="small")})
        col_qual.dataframe(
            _metric_table(snap["metrics"], QUALITY_LABELS),
            use_container_width=True, hide_index=True,
            column_config={"Metric": st.column_config.TextColumn("Profitability & Growth"),
                           "Value": st.column_config.TextColumn("", width="small")})
    except ValueError as e:
        st.warning(str(e))
    except Exception as e:
        st.error(f"Fetch failed for {ticker.upper()}: {e}")

# --- Peer comparison ---------------------------------------------------------------
st.markdown("## Peer Comparison")
compare_raw = st.text_input("Tickers, comma-separated", placeholder="e.g. MSFT, GOOGL, AMZN")
if compare_raw.strip():
    tickers = [t.strip().upper() for t in compare_raw.split(",") if t.strip()][:6]
    with st.spinner("Fetching…"):
        table = _comparison(tuple(tickers))
    st.dataframe(table, use_container_width=True)

# --- Watchlist ----------------------------------------------------------------------
st.markdown("## Watchlist")
watchlist = load_watchlist()
if not watchlist:
    st.info("Empty — add tickers you're evaluating with the button above.")
else:
    with st.spinner("Fetching watchlist fundamentals…"):
        table = _comparison(tuple(watchlist))
    st.dataframe(table, use_container_width=True)
    col_sel, col_rm = st.columns([4, 1])
    remove = col_sel.selectbox("Remove from watchlist", [""] + watchlist,
                               format_func=lambda t: t or "Select symbol to remove",
                               label_visibility="collapsed")
    if col_rm.button("Remove", disabled=not remove, use_container_width=True):
        remove_ticker(remove)
        _comparison.clear()
        st.rerun()
