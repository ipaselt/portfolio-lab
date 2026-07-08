"""Watchlist persistence — a plain JSON list of tickers at data/watchlist.json (gitignored)."""
import json
from pathlib import Path

WATCHLIST_PATH = Path("data") / "watchlist.json"


def load_watchlist():
    if not WATCHLIST_PATH.exists():
        return []
    return json.loads(WATCHLIST_PATH.read_text())


def save_watchlist(tickers):
    WATCHLIST_PATH.parent.mkdir(exist_ok=True)
    WATCHLIST_PATH.write_text(json.dumps(sorted(set(tickers)), indent=2))


def add_ticker(ticker):
    tickers = load_watchlist()
    ticker = ticker.upper().strip()
    if ticker and ticker not in tickers:
        tickers.append(ticker)
        save_watchlist(tickers)
    return load_watchlist()


def remove_ticker(ticker):
    tickers = [t for t in load_watchlist() if t != ticker.upper().strip()]
    save_watchlist(tickers)
    return tickers
