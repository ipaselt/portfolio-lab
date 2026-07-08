"""News feed for tickers, via yfinance (Yahoo Finance news — free, no API key).

Schema verified live 2026-07-08: each item nests under 'content' with title / summary /
pubDate (ISO8601 Z) / canonicalUrl.url / provider.displayName / contentType (STORY|VIDEO).
Chosen over a paid news API as the v1 default — swap the fetch layer here if coverage
proves too thin (planning/todo.md #12).
"""
from datetime import datetime, timezone

import yfinance as yf


def fetch_news(ticker, limit=8):
    """Return a list of {title, summary, url, provider, published, type} for a ticker.

    Malformed items are skipped rather than raising — Yahoo's feed is best-effort.
    """
    items = []
    for raw in yf.Ticker(ticker).news[:limit]:
        content = raw.get("content") or {}
        title = content.get("title")
        url = (content.get("canonicalUrl") or {}).get("url")
        if not title or not url:
            continue
        published = None
        pub_raw = content.get("pubDate")
        if pub_raw:
            try:
                published = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except ValueError:
                pass
        items.append({
            "ticker": ticker.upper(),
            "title": title,
            "summary": content.get("summary") or "",
            "url": url,
            "provider": (content.get("provider") or {}).get("displayName", "—"),
            "published": published,
            "type": content.get("contentType", "STORY"),
        })
    return items


def age_label(published):
    """'3h ago' / '2d ago' style label; empty string when the timestamp is missing."""
    if published is None:
        return ""
    delta = datetime.now(timezone.utc) - published
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return f"{max(1, int(delta.total_seconds() // 60))}m ago"
    if hours < 24:
        return f"{int(hours)}h ago"
    return f"{int(hours // 24)}d ago"
