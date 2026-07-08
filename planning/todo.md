# Task Queue — portfolio-lab

> **Non-orchestrated** — one session works this list top to bottom, no owner/session tags needed.
> Phases are sequenced on purpose: Phase 0 resolves two real unknowns (account access, IRA support)
> that could reshape Phase 1; Phase 1 is the smallest end-to-end useful thing (see your real
> portfolio in the dashboard); Phases 2-4 are the "broad research engine" the user asked for, built
> incrementally rather than all at once.

## Phase 0 — verify before building on top of it
- ⏳ **#1** Copy Schwab app credentials from `../trade-log/.env` into this project's `.env`, then run
  `python -m src.authenticate`. Confirms the OAuth flow works standalone here.
- ⏳ **#2** Inspect what `get_accounts_summary()` actually returns. Confirm: (a) does it include the
  Roth IRA and individual accounts, or only the options account trade-log was scoped to? (b) if IRA
  is missing, can the Schwab OAuth consent screen be re-run to add it, or does the Trader API not
  expose retirement accounts at all (checked against real behavior, not assumed)? (c) do the assumed
  JSON field names in `schwab_client.py`/`portfolio.py` match reality — fix them if not.
- ⏳ **#3** If Roth IRA truly isn't reachable via the API: decide the fallback (manual balance/holdings
  entry for that account vs. leaving it untracked) — user decision, don't assume.

## Phase 1 — portfolio tracking MVP
- ⏳ **#4** Fix `positions_dataframe()`/`get_accounts_summary()` against real field names (from #2).
- ⏳ **#5** Dashboard: positions table + allocation-by-symbol chart + total unrealized P&L, across
  every account the token can see, labeled by account type.
- ⏳ **#6** Cost-basis / performance view: per-position and total unrealized gain/loss, % of portfolio.

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
