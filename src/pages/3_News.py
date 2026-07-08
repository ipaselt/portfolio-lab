"""News page — headlines for holdings and watchlist tickers."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.research.news import age_label, fetch_news
from src.watchlist import load_watchlist

st.set_page_config(page_title="News — Portfolio Lab", layout="wide")
st.title("News")


@st.cache_data(ttl=900, show_spinner=False)
def _news(ticker, limit):
    return fetch_news(ticker, limit)


@st.cache_data(ttl=900, show_spinner=False)
def _holding_symbols():
    try:
        from src.schwab_client import get_accounts_summary, get_client
        accounts = get_accounts_summary(get_client())
        return sorted({
            p["instrument"]["symbol"]
            for a in accounts for p in a["positions"]
            if p.get("instrument", {}).get("assetType") in ("EQUITY", "COLLECTIVE_INVESTMENT")
        })
    except Exception:
        return []


holdings = _holding_symbols()
watchlist = load_watchlist()
universe = sorted(set(holdings) | set(watchlist))

if not universe:
    st.info("No holdings or watchlist tickers found — add some on the Research page.")
    st.stop()

scope = st.radio("Show news for", ["All holdings + watchlist", "One ticker"], horizontal=True)

if scope == "One ticker":
    ticker = st.selectbox("Ticker", universe)
    tickers = [ticker]
    per_ticker = 10
else:
    tickers = universe
    per_ticker = 3

with st.spinner("Fetching headlines…"):
    all_items = []
    for t in tickers:
        try:
            all_items.extend(_news(t, per_ticker))
        except Exception:
            continue  # one flaky ticker shouldn't sink the feed

# Newest first; undated items sink to the bottom.
all_items.sort(key=lambda i: (i["published"] is None,
                              -(i["published"].timestamp() if i["published"] else 0)))

if not all_items:
    st.info("No headlines right now.")
def _md_safe(text):
    # Streamlit markdown renders $…$ as LaTeX — escape dollars in news text.
    return text.replace("$", "\\$")


for item in all_items:
    tag = " · 🎬 video" if item["type"] == "VIDEO" else ""
    summary = _md_safe(item["summary"][:280] + ("…" if len(item["summary"]) > 280 else ""))
    st.markdown(
        f"**`{item['ticker']}`  [{_md_safe(item['title'])}]({item['url']})**  \n"
        f"{summary}  \n"
        f"*{item['provider']} · {age_label(item['published'])}{tag}*")
    st.divider()
