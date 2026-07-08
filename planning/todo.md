# Task Queue — portfolio-lab

> **Non-orchestrated** — one session works this list top to bottom, no owner/session tags needed.
> Phases are sequenced on purpose: Phase 0 resolves two real unknowns (account access, IRA support)
> that could reshape Phase 1; Phase 1 is the smallest end-to-end useful thing (see your real
> portfolio in the dashboard); Phases 2-4 are the "broad research engine" the user asked for, built
> incrementally rather than all at once.

## Phase 0 — verify before building on top of it
- ✅ **#1** Credentials copied, `python -m src.authenticate` works standalone here (2026-07-08).
- ✅ **#2** Verified live: all 3 accounts visible (the OAuth CONSENT SCREEN scopes account access —
  user re-consented with all accounts checked). Roth IRA IS exposed by the Trader API. Field names
  matched as assumed except: `type` is only CASH/MARGIN (→ `ACCOUNT_LABELS` in `.env`), and
  zero-position accounts omit the `positions` key entirely.
- ✅ **#3** Moot — Roth IRA is reachable, no fallback needed.

## Phase 1 — portfolio tracking MVP
- ✅ **#4** Client verified against real field names; account labels wired (2026-07-08).
- ✅ **#5** Dashboard verified live in browser: positions table + allocation chart + total P&L across
  all 3 labeled accounts. Fixed en route: per-position P&L % now divides by cost basis, not market
  value (regression test added).
- ⏳ **#6** Cost-basis / performance view: per-account subtotals, % of portfolio per position,
  maybe a P&L-by-account bar chart.

## Phase 2 — fundamentals research (the first "find new stocks" module)
- ⏳ **#7** `src/research/fundamentals.py` — pull financials + valuation ratios (P/E, P/B, EV/EBITDA,
  margins, growth) for an arbitrary ticker via `yfinance`.
- ⏳ **#8** Dashboard: "Research" page — enter a ticker, see its fundamentals/valuation snapshot next
  to a couple of peers.
- ⏳ **#9** Watchlist: save tickers you're evaluating, separate from actual holdings.

## Phase 3 — technicals
- ⏳ **#10** `src/research/technicals.py` — price history, moving averages, RSI, relative strength vs.
  a benchmark.
- ⏳ **#11** Dashboard: chart view per ticker (holdings + watchlist).

## Phase 4 — news & sentiment
- ⏳ **#12** `src/research/news.py` — headline/filing feed (10-K/10-Q/8-K, analyst actions) for
  holdings + watchlist. Needs a data-source decision (free RSS vs. a paid news API) — revisit once
  Phases 1-3 are working and it's clear what's actually useful day-to-day.
- ⏳ **#13** Dashboard: news feed panel.

✅ Completed → `../memory/completed-tasks.md`.
