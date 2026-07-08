"""Fundamentals snapshot for a ticker, via yfinance.

Field availability verified live against yfinance 2026-07-08 (all fields below present for AAPL;
sparse tickers like OTC microcaps may return None for many — the dashboard shows those as "—").
Data is Yahoo-sourced and can lag or be wrong for thinly traded names; this is a research aid,
not an execution-grade feed.
"""
import pandas as pd
import yfinance as yf

# (yfinance info key, display label, format)
# format: 'x' = ratio like 24.5x · '%' = 0.253 → 25.3% · '%asis' = 2.52 → 2.52% (already percent)
#         · '$' = dollar amount · '$big' = abbreviated (B/T) · 'raw'
# NOTE dividendYield is '%asis': verified live 2026-07-08 (KO raw=2.52 vs dividendRate/price=2.5%)
# — yfinance returns it pre-multiplied, unlike margins/growth which are true fractions.
FIELDS = [
    ("currentPrice", "Price", "$"),
    ("marketCap", "Market cap", "$big"),
    ("trailingPE", "P/E (ttm)", "x"),
    ("forwardPE", "P/E (fwd)", "x"),
    ("priceToBook", "P/B", "x"),
    ("enterpriseToEbitda", "EV/EBITDA", "x"),
    ("grossMargins", "Gross margin", "%"),
    ("operatingMargins", "Op margin", "%"),
    ("profitMargins", "Net margin", "%"),
    ("revenueGrowth", "Revenue growth (yoy)", "%"),
    ("earningsGrowth", "Earnings growth (yoy)", "%"),
    ("returnOnEquity", "ROE", "%"),
    ("debtToEquity", "Debt/Equity", "raw"),
    ("freeCashflow", "Free cash flow", "$big"),
    ("dividendYield", "Dividend yield", "%asis"),
    ("trailingEps", "EPS (ttm)", "$"),
    ("fiftyTwoWeekLow", "52w low", "$"),
    ("fiftyTwoWeekHigh", "52w high", "$"),
    ("targetMeanPrice", "Analyst target (mean)", "$"),
    ("recommendationKey", "Analyst consensus", "raw"),
]


def fetch_snapshot(ticker):
    """Return {'name', 'sector', 'industry', 'metrics': {label: raw_value}} for a ticker.

    Raises ValueError if the ticker returns no usable data.
    """
    info = yf.Ticker(ticker).info
    # Yahoo returns a near-empty dict (or one with no price data) for unknown symbols.
    if not info or info.get("currentPrice") is None and info.get("regularMarketPrice") is None:
        raise ValueError(f"No data for ticker {ticker!r} — check the symbol.")
    return {
        "symbol": ticker.upper(),
        "name": info.get("longName") or info.get("shortName") or ticker.upper(),
        "sector": info.get("sector", "—"),
        "industry": info.get("industry", "—"),
        "metrics": {label: info.get(key) for key, label, _fmt in FIELDS},
    }


def format_value(label, value):
    """Human-format one metric value by its FIELDS format code."""
    if value is None:
        return "—"
    fmt = next((f for _k, lbl, f in FIELDS if lbl == label), "raw")
    if fmt == "x":
        return f"{value:,.1f}x"
    if fmt == "%":
        return f"{value * 100:,.1f}%"
    if fmt == "%asis":
        return f"{value:,.2f}%"
    if fmt == "$":
        return f"${value:,.2f}"
    if fmt == "$big":
        for divisor, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M")]:
            if abs(value) >= divisor:
                return f"${value / divisor:,.2f}{suffix}"
        return f"${value:,.0f}"
    return str(value)


def comparison_table(tickers):
    """Fetch snapshots for several tickers → DataFrame with metrics as rows, tickers as columns.

    Tickers that fail to fetch get a column of '—' with '(no data)' in the name row rather than
    sinking the whole table.
    """
    columns = {}
    for ticker in tickers:
        try:
            snap = fetch_snapshot(ticker)
            col = {"Name": snap["name"], "Sector": snap["sector"]}
            col.update({lbl: format_value(lbl, val) for lbl, val in snap["metrics"].items()})
        except Exception:
            col = {"Name": "(no data)", "Sector": "—"}
            col.update({lbl: "—" for _k, lbl, _f in FIELDS})
        columns[ticker.upper()] = col
    return pd.DataFrame(columns)
