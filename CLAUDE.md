# CLAUDE.md — portfolio-lab

Tracks long-term investment holdings (Roth IRA + individual brokerage, via Schwab) and provides a
research engine (fundamentals, technicals, news) for evaluating current holdings and finding new
stock ideas. Local web dashboard (Streamlit). Home base: `projects/portfolio-lab/` (the repo root =
the main-branch checkout). **Non-orchestrated**: single-session build, commit straight to main — see
`memory/decisions.md` for why.

> Auto-loads when an agent works in this project. Apply the method in
> `~/Developer/guide-setup/van-clief/VAN-CLIEF-RULES.md`; stamp from `…/van-clief/templates/` only if
> this graduates to multi-session orchestration later.

## Workspace Map
```
portfolio-lab/                   — THE git repo (this folder = the main-branch checkout)
├── CLAUDE.md      — this file · CONTEXT.md — working detail (load tables, process, do-nots)
├── planning/      — todo.md (phased backlog) · progress.md (rollup)
├── memory/        — primer.md (state) · decisions.md (append-only)
├── src/           — production code (plain repo: commit straight to main)
├── tests/         — pytest
└── .env.example   — Schwab app key/secret template (real .env is gitignored)
```

## Stack · Routing · Commands
- **Stack:** Python 3 · [`schwab-py`](https://github.com/alexgolec/schwab-py) (Schwab Trader API + OAuth, read-only)
  · `yfinance` (market data / fundamentals for research) · `pandas` · `plotly` · `streamlit` (dashboard)
- **Routing:** Schwab client → `src/schwab_client.py` · portfolio aggregation → `src/portfolio.py` ·
  research modules → `src/research/` (fundamentals/technicals/news, built incrementally) · dashboard →
  `src/dashboard.py`
- **Commands:** `streamlit run src/dashboard.py` (dashboard) · `python -m src.authenticate` (Schwab
  (re-)auth, ~weekly) · `pytest` (test) — venv at `.venv/`

## Conventions
- Spec before code; one fact, one location; lowercase-hyphen naming.
- Secrets in `.env` (gitignored). Never hardcode the Schwab app key/secret or account numbers.
- This project reuses the **same registered Schwab app** (key/secret) as `../trade-log/` — it's one
  Schwab Developer Portal app per person, not per project. Its own `.env`/token file are separate and
  self-contained (no cross-project imports), per the dev-root convention.

## Current State
- Skeleton scaffolded, schema-uncertain first-cut code written (schwab_client.py / portfolio.py /
  dashboard.py) — **not yet run against live data**, since account/position field names in Schwab's
  response are assumed from `schwab-py` docs, not verified live from this session. Full backlog in
  `planning/todo.md`. See `memory/primer.md` for the up-to-date state.
- **Two open unknowns, first task in the queue:** (1) whether the existing Schwab OAuth consent
  already covers the Roth IRA + individual accounts, or only the options account it was granted for;
  (2) whether the Schwab Trader API exposes retirement (Roth IRA) account data at all — some brokers
  restrict API access to taxable accounts. Both resolve by running `python -m src.authenticate` here
  and inspecting what `get_accounts_summary()` returns.

## Avoid
- Never place, modify, or cancel orders — this project is **read-only** against Schwab (positions,
  balances, history only).
- Don't hand-roll Schwab OAuth; reuse the `schwab-py` token flow already proven in `trade-log`.
- Never commit `.env`, the token file, or real account numbers.
- No automated trade execution of any kind, ever — research and tracking only.
