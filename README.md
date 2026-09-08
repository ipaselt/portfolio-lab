# Portfolio Lab

A local, read-only dashboard for long-term investing. It pulls live positions and balances from every
Schwab account the user has authorized (Roth IRA and individual brokerage) through the Schwab Trader
API, aggregates them into a single portfolio view with per-account performance, and pairs that with a
research engine — fundamentals snapshots and peer comparisons, technical charts, and a news feed —
for evaluating current holdings and screening new ideas. Built in Python with Streamlit; runs
entirely on your machine against your own brokerage credentials.

## What it does

- **Overview** — total account value, invested market value and unrealized P&L (dollar and percent);
  a card per account; a per-account performance table (market value, cost basis, P&L, share of
  portfolio) with a P&L-by-account bar chart; a positions table across all accounts; allocation by
  symbol. Prompts you to re-authenticate if the Schwab token has expired.
- **Research** — a 20-metric fundamentals snapshot for any ticker (valuation and price on one side,
  profitability and growth on the other); a side-by-side peer comparison for up to six tickers; a
  persistent watchlist with the same comparison table and add/remove controls.
- **Charts** — candlestick price history with SMA-50/200 overlays and a Wilder RSI-14 subplot, a
  relative-strength line versus SPY (rebased cumulative-return ratio), and a summary strip (last
  close, period high/low, RSI). The ticker picker is seeded from your live holdings plus watchlist;
  periods from 3M to 5Y.
- **News** — Yahoo Finance headlines for all holdings and watchlist tickers, or one ticker at a time,
  sorted newest-first with provider and age labels. Research pages cache upstream calls for 15 minutes
  and still work from typed or watchlist tickers if Schwab auth is stale.

## Architecture

| Module | Role |
|--------|------|
| `src/app.py` | Entry point: anchors to the project root, injects the design system, `st.navigation` shell |
| `src/views/` | One file per page: `overview`, `research`, `charts`, `news` |
| `src/schwab_client.py` | Read-only Schwab Trader API client (via `schwab-py`); enumerates every consented account |
| `src/authenticate.py` | One-command OAuth (re-)auth with a local HTTPS loopback capture and a manual-paste fallback |
| `src/portfolio.py` | Flattens positions across accounts, computes P&L / cost basis / allocation, builds portfolio charts |
| `src/research/` | `fundamentals` (yfinance snapshot + formatting), `technicals` (SMA, RSI, relative strength in pure pandas), `news` |
| `src/watchlist.py` | JSON-backed watchlist persistence |
| `src/ui.py` | Design system: color tokens, global CSS, Plotly template, number formatters |
| `tests/` | pytest suite over the aggregation math, indicators, formatters and watchlist |

## Hard problems solved / things I learned

**Verify money math against live data, not just against tests.** The first cut of per-position P&L
percent divided unrealized P&L by market value. It passed the synthetic tests and produced a
nonsensical figure (beyond -100% on a long position) the moment it ran against real Schwab data.
The correct denominator is cost basis, which Schwab does not return directly and is derived as
`market_value - unrealized_pl`. The fix is pinned by
`test_unrealized_pl_pct_is_relative_to_cost_basis`, and the project's rule since then is that
anything touching the live response schema is run once against real data before it counts as done.

**The Schwab API does not know what a Roth IRA is.** `securitiesAccount.type` is only `CASH` or
`MARGIN`; nothing in the response distinguishes a retirement account from a taxable one. Human-readable
account names therefore come from an `ACCOUNT_LABELS` setting in `.env` (`1234:Individual,5678:Roth IRA`,
keyed on the last four digits), and the client masks account numbers before they reach the UI.
Related discovery: which accounts the API can see is decided on Schwab's OAuth consent screen at
login time, not by the developer-app registration — a token that only showed one account was fixed by
re-authenticating and ticking every account.

**Free data sources have inconsistent units.** In yfinance, `dividendYield` arrives pre-multiplied
(2.52 means 2.52%) while margins and growth rates are true fractions (0.253 means 25.3%). Each field in
the fundamentals module carries an explicit format code, and the two scales are regression-tested so a
future refactor cannot silently multiply a yield by 100 again. Likewise, ETFs come back from Schwab as
`COLLECTIVE_INVESTMENT`, not `EQUITY`, and zero-position accounts omit the `positions` key entirely.

**Small rendering traps compound in a finance UI.** Streamlit interprets `$...$` in markdown as
LaTeX, so any headline or summary containing two dollar amounts rendered as math until feed text was
escaped. A global font override silently broke Material icons. Metric cards would ellipsize dollar
figures, which is the one thing a portfolio dashboard must never do.

## Design

The UI follows a design system derived from Linear's product language, vendored as a style contract in
`docs/linear.DESIGN.md` and implemented once in `src/ui.py`: a near-black canvas, a surface ladder with
hairline borders, a single lavender accent used sparingly, Inter with tabular numerals, and green/red
reserved for P&L semantics. Tokens drive both the global CSS and a registered Plotly template, so tables,
metric cards and charts read as one product.

## Stack

Python 3.11 · Streamlit · pandas · Plotly · [`schwab-py`](https://github.com/alexgolec/schwab-py) (Schwab Trader API + OAuth) · yfinance · python-dotenv · pytest

## Running it

You need a Schwab brokerage account and an approved app on the
[Schwab Developer Portal](https://developer.schwab.com) (Trader API, individual). The app's registered
callback URL must match `SCHWAB_CALLBACK_URL` exactly.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  |  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env              # then fill in SCHWAB_APP_KEY, SCHWAB_APP_SECRET, ACCOUNT_LABELS
python -m src.authenticate        # opens a browser, captures the OAuth redirect, caches a token
streamlit run src/app.py
```

`authenticate` prints every account the new token can see so you can confirm the right ones were
consented. Schwab refresh tokens expire after roughly seven days and can only be renewed through a
browser login, so expect to re-run that step about weekly; the Overview page tells you when.
`.env`, the token file and the watchlist are gitignored.

## Tests

```bash
python -m pytest -q
```

25 tests, all passing: portfolio aggregation (cost-basis P&L, per-account rollups, allocation),
technical indicators (SMA, RSI bounds and warm-up, relative-strength alignment), fundamentals
formatting (fraction vs pre-multiplied percent), news age labels, and watchlist persistence.

---

Read-only against Schwab: this project never places, modifies or cancels orders. Market and
fundamentals data come from Yahoo Finance and may lag or be wrong. Nothing here is financial advice.
