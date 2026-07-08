"""News — headlines for holdings and watchlist tickers, card layout."""
import html

import streamlit as st

from src.research.news import age_label, fetch_news
from src.ui import page_header
from src.watchlist import load_watchlist

page_header("News", "Yahoo Finance headlines · holdings + watchlist · 15-minute cache")


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

scope = st.radio("Scope", ["All holdings + watchlist", "One ticker"],
                 horizontal=True, label_visibility="collapsed")

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

all_items.sort(key=lambda i: (i["published"] is None,
                              -(i["published"].timestamp() if i["published"] else 0)))

if not all_items:
    st.info("No headlines right now.")

for item in all_items:
    title = html.escape(item["title"])
    summary = html.escape(item["summary"][:260] + ("…" if len(item["summary"]) > 260 else ""))
    video = " · Video" if item["type"] == "VIDEO" else ""
    st.markdown(f"""<div class="pl-news-card">
<span class="pl-ticker-badge">{item['ticker']}</span><a href="{item['url']}" target="_blank">{title}</a>
<div class="pl-news-summary">{summary}</div>
<div class="pl-news-meta">{html.escape(item['provider'])} · {age_label(item['published'])}{video}</div>
</div>""", unsafe_allow_html=True)
