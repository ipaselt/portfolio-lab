# Primer — portfolio-lab
*Rewrite each session. Last updated: 2026-07-08 (evening).*

## State
- **✅ ALL FOUR PHASES WORKING, live-verified (2026-07-08).** 4-page Streamlit app:
  **dashboard** (accounts, per-account performance, positions, allocation) · **Research**
  (fundamentals snapshot, peer compare, watchlist) · **Charts** (candlestick + SMA 50/200 + RSI +
  rel-strength vs SPY, picker seeded from live holdings + watchlist) · **News** (aggregated Yahoo
  feed). 3 accounts (Individual ...XXXX, Roth IRA ...XXXX, Options ...XXXX), 10 positions. Tests
  25/25. 6 local commits, no remote.
- **yfinance gotchas (verified live, don't relearn):** `dividendYield` is pre-multiplied
  (2.52 = 2.52%) while margins/growth are fractions; news items nest under `content` with
  `canonicalUrl.url`; Schwab ETFs are assetType `COLLECTIVE_INVESTMENT`, not EQUITY. Streamlit
  renders `$…$` as LaTeX — escape dollars in any rendered feed text.
- **Roth IRA question ANSWERED:** the Trader API DOES expose the Roth IRA — the user just had to
  check ALL accounts on the Schwab OAuth consent screen (that screen, not the app registration, is
  what scopes account visibility). Re-run `python -m src.authenticate` weekly (~7-day refresh token,
  same as trade-log; must run in a real terminal, needs browser + stdin).
- **Live-schema gotchas (don't relearn):** `securitiesAccount.type` = CASH/MARGIN only — NOTHING in
  the API says Roth-vs-Individual, hence `ACCOUNT_LABELS` in `.env` (last4:label). Zero-position
  accounts have NO `positions` key. Other field names matched schwab-py docs as assumed.
- **Bug fixed during live verify:** per-position `unrealized_pl_pct` originally divided by market
  value → nonsense (-127% on a long); now divides by cost basis (= market_value − unrealized_pl),
  regression-tested.
- **Professional redesign (2026-07-08 evening):** restructured to `src/app.py` (st.navigation entry)
  + `src/views/{overview,research,charts,news}.py` + `src/ui.py` (design tokens, global CSS, plotly
  template, Inter/tabular-nums). `src/dashboard.py` + `src/pages/` are GONE. Then **rethemed to
  Linear's design language** — style contract vendored at `docs/linear.DESIGN.md`; single lavender
  accent #5E6AD2, canvas #010102, surface ladder + hairlines; tokens are PRIMARY/PRIMARY_LIGHT/
  PRIMARY_MUTED/GREEN/RED in `src/ui.py` (BLUE/AMBER/VIOLET no longer exist). Gotchas: the global
  font CSS must not clobber `stIconMaterial` (Material icons render as garbled text); metric values
  need the no-ellipsis override + clamp() sizing and SHORT delta strings; NumberColumn
  `format="dollar"` gives thousands separators (printf `$%.2f` does not).
- **Preview/launch note:** the dashboard launch config lives in `~/Developer/.claude/launch.json`
  ("portfolio-dashboard" → `src/app.py`) because Preview reads the SESSION root's launch.json, not
  the project's; `app.py` chdir's to the project root at import so relative .env/token paths work
  from any cwd. Streamlit does NOT hot-reload imported src/ modules — restart after editing them.
- **Not yet done:** no GitHub remote (local commits only, user hasn't asked to publish); global git
  identity set 2026-07-08 (ipase / ipaseltiner@gmail.com).

## Next
`planning/todo.md` #6 (cost-basis/performance view polish) → Phase 2 (fundamentals research module).
