# portfolio-lab — CONTEXT.md

Working detail for this project (`projects/portfolio-lab/`). Last updated: 2026-07-08.

> **Non-orchestrated.** No planner/worker split, no PR-per-task, no `.orchestrated` marker — one
> session builds and commits straight to `main`, same pattern as `../trade-log/`. Reason logged in
> `memory/decisions.md`. If the backlog grows into several independent, parallelizable chunks of work
> (e.g. building 3 research modules at once), graduate to full **VAN-CLIEF §9** multi-session
> orchestration then — stamp from `guide-setup/van-clief/templates/new-project/` at that point.

## What to Load
| Task | Load | Skip |
|------|------|------|
| Resume / "what's next" | `memory/primer.md` → your next `⏳` in `planning/todo.md` | — |
| Cross-session state / why a call was made | `memory/decisions.md` | code |
| Schwab auth / account access | `src/schwab_client.py` + `src/authenticate.py` docstrings | — |
| Add a research module (fundamentals/technicals/news) | `src/research/` + wire into `src/dashboard.py` | other research modules until they exist |

## The Process
Single session, plain repo. Read `CLAUDE.md` + this file + `memory/primer.md` at the start of a
session. Work through `planning/todo.md` top to bottom (phased — earlier phases unblock later ones).
Commit directly to `main` after each working increment; update `memory/primer.md` when state changes
meaningfully (not every commit). No PRs, no reviewer/verifier sessions for this project's normal flow —
still get an independent review pass (`/code-review`) before any push that touches money-adjacent
logic (position math, P&L, valuation formulas), per the global review-before-push rule.

**Verification is real, not typechecking:** anything touching the live Schwab response (field names,
shapes) must be run once against real data and the assumed schema corrected — don't report a Schwab
integration task done on the strength of it merely running without a stack trace against empty/mock data.

## Skills & Tools
| Skill / Tool | When | Purpose |
|--------------|------|---------|
| Preview (`mcp__Claude_Preview__*`) | verifying the Streamlit dashboard in-browser | DOM-aware, per-session — try FIRST |
| computer-use | only when Preview can't reach it | shared physical screen — mutex-gated |

## What NOT to Do
- Never place, modify, or cancel a Schwab order — read-only, always.
- Don't assume Schwab's JSON field names without checking a live response — they're first-cut guesses
  in `schwab_client.py`/`portfolio.py` until verified (see `CLAUDE.md` Current State).
- Never commit `.env`, `.schwab_token.json`, or real account numbers.
- Don't import code from `../trade-log/` directly (self-contained projects) — copy the pattern, not
  the module.
