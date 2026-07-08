"""Research page — fundamentals snapshot + peer comparison + watchlist."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.research.fundamentals import FIELDS, comparison_table, fetch_snapshot, format_value
from src.watchlist import add_ticker, load_watchlist, remove_ticker

st.set_page_config(page_title="Research — Portfolio Lab", layout="wide")
st.title("Research")


@st.cache_data(ttl=900, show_spinner=False)
def _snapshot(ticker):
    return fetch_snapshot(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def _comparison(tickers):
    return comparison_table(list(tickers))


# --- Single-ticker snapshot ---------------------------------------------------
st.subheader("Ticker snapshot")
col_in, col_btn = st.columns([3, 1])
ticker = col_in.text_input("Ticker", placeholder="e.g. MSFT", label_visibility="collapsed").strip()
add_clicked = col_btn.button("Add to watchlist", disabled=not ticker)

if add_clicked and ticker:
    add_ticker(ticker)
    st.toast(f"{ticker.upper()} added to watchlist")

if ticker:
    try:
        with st.spinner(f"Fetching {ticker.upper()}…"):
            snap = _snapshot(ticker.upper())
        st.markdown(f"### {snap['name']}  \n{snap['sector']} · {snap['industry']}")
        metrics = list(snap["metrics"].items())
        for row_start in range(0, len(metrics), 5):
            cols = st.columns(5)
            for col, (label, value) in zip(cols, metrics[row_start:row_start + 5]):
                col.metric(label, format_value(label, value))
    except ValueError as e:
        st.warning(str(e))
    except Exception as e:
        st.error(f"Fetch failed for {ticker.upper()}: {e}")

# --- Peer comparison ----------------------------------------------------------
st.subheader("Compare tickers")
compare_raw = st.text_input("Tickers, comma-separated", placeholder="e.g. MSFT, GOOGL, AMZN")
if compare_raw.strip():
    tickers = [t.strip().upper() for t in compare_raw.split(",") if t.strip()][:6]
    with st.spinner("Fetching…"):
        table = _comparison(tuple(tickers))
    st.dataframe(table, use_container_width=True)

# --- Watchlist ----------------------------------------------------------------
st.subheader("Watchlist")
watchlist = load_watchlist()
if not watchlist:
    st.info("Empty — add tickers you're evaluating with the button above.")
else:
    with st.spinner("Fetching watchlist fundamentals…"):
        table = _comparison(tuple(watchlist))
    st.dataframe(table, use_container_width=True)
    remove = st.selectbox("Remove from watchlist", [""] + watchlist,
                          format_func=lambda t: t or "(choose)")
    if remove and st.button(f"Remove {remove}"):
        remove_ticker(remove)
        _comparison.clear()
        st.rerun()
