# portfolio-lab

Tracks long-term holdings (Roth IRA + individual brokerage, via Schwab) and helps research new stock
ideas (fundamentals, technicals, news) via a local Streamlit dashboard. Read-only against Schwab —
never places, modifies, or cancels orders.

## Setup

1. `python -m venv .venv` then activate it (`.venv\Scripts\activate` on Windows, `source .venv/bin/activate` elsewhere).
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in `SCHWAB_APP_KEY` / `SCHWAB_APP_SECRET` — same values as
   `../trade-log/.env`, since it's one registered Schwab app per person. Keep `SCHWAB_CALLBACK_URL`
   identical to what's registered on that app.
4. `python -m src.authenticate` — opens a browser to log in to Schwab, caches a token, and prints
   which accounts the token can see. **Check that your Roth IRA and individual account show up here**
   — if only the options account appears, the OAuth consent needs to be re-granted with the other
   accounts selected (or the Trader API may not expose IRAs at all — see `planning/todo.md` #2-#3).
5. `streamlit run src/app.py` — opens the dashboard in your browser.

The Schwab refresh token expires roughly every 7 days; re-run step 4 when the dashboard reports an
auth error.

## Status

See `memory/primer.md` for current state and `planning/todo.md` for the working backlog.
