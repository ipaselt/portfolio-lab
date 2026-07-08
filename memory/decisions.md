# Decisions — portfolio-lab (append-only)

## 2026-07-08 — Non-orchestrated at kickoff
Considered full Van Clief multi-session orchestration (planner + worker + reviewer/verifier sessions,
PR-per-task, GitHub review-lifecycle labels) vs. a single build session, per `guide-setup/van-clief/
templates/new-project/setup-checklist.md`. Chose **non-orchestrated**, mirroring `../trade-log/`:
there is no spec yet to parallelize against, and orchestration's overhead (labels, reviewer/verifier
sessions the user would have to manually open — an agent can't spawn new sessions) buys nothing before
a concrete, parallelizable backlog exists. Revisit if the project grows into several independent
research modules that could genuinely be built at once.

## 2026-07-08 — Reuse trade-log's Schwab app credentials, not a new app
The Schwab Developer Portal registers apps per person, not per project — `trade-log` already has an
"Trader API – Individual" app approved and working (`SCHWAB_APP_KEY`/`SCHWAB_APP_SECRET` in its
`.env`). Registering a second app would mean a second approval wait for no real isolation benefit
(same person, same brokerage login). portfolio-lab gets its own `.env`/`.schwab_token.json` (own OAuth
session, own callback capture), but the same underlying app key/secret. Projects stay code-isolated
(no cross-project imports) — only the credential values are shared, copied not referenced.

## 2026-07-08 — Streamlit for the dashboard, not FastAPI+React
User wants a local web dashboard and a broad, incrementally-built research engine. Streamlit gives a
real interactive UI (tables, charts, multi-page nav) in pure Python with no separate frontend build —
fastest to extend as new research modules (fundamentals → technicals → news) get added over many
sessions. A separate API + SPA frontend would be more "production," but there's no case for that
overhead in a single-user local tool.

## 2026-07-08 — yfinance for market/fundamentals data at this stage
Free, no API key, good enough for fundamentals + price history to build Phase 1-3 against. Revisit if
a specific gap shows up (e.g. real-time quotes, deeper fundamentals, or reliable news/filings — Phase
4 already flags a paid-API decision point for news/sentiment specifically).
