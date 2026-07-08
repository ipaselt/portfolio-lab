# Primer — portfolio-lab
*Rewrite each session. Last updated: 2026-07-08.*

## State
- **Scaffolded, not yet run (2026-07-08).** Skeleton + first-cut code exist: `src/schwab_client.py`
  (get_client + get_accounts_summary, reads ALL linked accounts — unlike trade-log's client, which
  hardcodes `accounts[0]`), `src/authenticate.py` (copied from trade-log's proven in-process HTTPS
  callback flow — the standard schwab-py/Flask auto-capture is broken on this Windows box, don't
  rediscover that), `src/portfolio.py` (positions → DataFrame + allocation chart), `src/dashboard.py`
  (Streamlit entrypoint).
- **Unverified against live data:** the Schwab JSON field names in `schwab_client.py`/`portfolio.py`
  (`securitiesAccount`, `positions`, `currentBalances`, etc.) are written from `schwab-py` docs/
  trade-log's pattern, not confirmed against a real response from this project. First run will likely
  need field-name fixes — expected, not a bug to be surprised by.
- **Not yet answered:** does the existing Schwab app's OAuth consent (currently scoped to the options
  account for trade-log) already cover the user's Roth IRA + individual brokerage account, or does
  consent need to be re-granted per account? Does the Schwab Trader API expose Roth IRA data at all?
  → `planning/todo.md` #1-#3.
- **Not yet done:** `.env` not created (needs the user's real Schwab app key/secret, same ones as
  `trade-log/.env` — same registered app), Python venv not created, dependencies not installed, no git
  commits yet.

## Next
Start at `planning/todo.md` #1.
