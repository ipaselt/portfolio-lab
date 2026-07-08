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
- ✅ **#7** `src/research/fundamentals.py` — 20 metrics via yfinance, live-verified. Gotcha: yfinance
  `dividendYield` comes pre-multiplied (2.52 = 2.52%), unlike margins/growth fractions (2026-07-08).
- ✅ **#8** Research page: ticker snapshot + peer comparison table (2026-07-08).
- ✅ **#9** Watchlist: JSON at `data/watchlist.json` (gitignored), add/remove from Research page
  (2026-07-08).

## Phase 3 — technicals
- ✅ **#10** `src/research/technicals.py` — SMA, Wilder RSI, relative strength vs benchmark; 7 unit
  tests (2026-07-08).
- ✅ **#11** Charts page: candlestick + SMA 50/200 + RSI + rel-strength-vs-SPY; picker seeded from
  live holdings (ETFs = assetType `COLLECTIVE_INVESTMENT`) + watchlist (2026-07-08).

## Phase 4 — news & sentiment
- ✅ **#12** `src/research/news.py` — yfinance/Yahoo news (free, no key) chosen as the v1 source;
  swap the fetch layer if coverage proves thin. SEC-filings-specific feed NOT included (2026-07-08).
- ✅ **#13** News page: aggregated holdings+watchlist feed, newest first (2026-07-08).

## Ideas (unscheduled)
- ⏳ **#14** SEC filings feed (10-K/10-Q/8-K via EDGAR RSS) — the filings half of the original #12.
- ⏳ **#15** Screener: rank a universe (e.g. S&P 500) by fundamentals criteria to surface candidates.
- ⏳ **#16** Historical portfolio value tracking (snapshot per day → performance-over-time chart).
- ⏳ **#17** GitHub remote + review-before-push flow (money-math review gate), if/when user wants it.

✅ Completed → `../memory/completed-tasks.md`.
