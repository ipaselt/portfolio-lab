"""Schwab Trader API client — read-only. Never places, modifies, or cancels orders.

Reads positions and balances across EVERY account this token's OAuth consent covers, unlike
trade-log's client, which only ever looks at accounts[0] (fine there — it only cares about one
account's option trades).

UNVERIFIED: the JSON shape below (`securitiesAccount`, `positions`, `currentBalances`, ...) is
written from schwab-py's docs and trade-log's working transaction-history code, not confirmed
against a live positions response from this project. Run `python -m src.authenticate` and inspect
the printed summary; fix field names here if they don't match (see planning/todo.md #2).
"""
import os

from dotenv import load_dotenv
from schwab.auth import client_from_token_file

load_dotenv()


class ReauthNeeded(SystemExit):
    """Raised when the Schwab token is missing or expired — user must re-authenticate."""


def get_client():
    """Return a schwab-py client from the cached token — headless, never opens a browser.

    The access token auto-refreshes off the cached refresh token. When the refresh token itself
    expires (~7 days) or is missing, this fails cleanly; the fix is `python -m src.authenticate`.
    """
    api_key = os.environ["SCHWAB_APP_KEY"]
    app_secret = os.environ["SCHWAB_APP_SECRET"]
    token_path = os.environ.get("SCHWAB_TOKEN_PATH", ".schwab_token.json")

    if not api_key or not app_secret:
        raise SystemExit(
            "Missing SCHWAB_APP_KEY / SCHWAB_APP_SECRET. Fill them into .env first."
        )
    if not os.path.exists(token_path):
        raise ReauthNeeded(
            f"No Schwab token at {token_path}. Run: python -m src.authenticate"
        )

    return client_from_token_file(token_path, api_key, app_secret)


def get_accounts_summary(client):
    """Return every account this token can see: type, masked number, positions, balances.

    This is the verification step for planning/todo.md #2 — run it and check whether the Roth
    IRA and individual account actually show up, not just the options account.
    """
    resp = client.get_accounts(fields=[client.Account.Fields.POSITIONS])
    resp.raise_for_status()

    accounts = []
    for entry in resp.json():
        acct = entry["securitiesAccount"]
        account_number = acct.get("accountNumber", "")
        accounts.append({
            "account_number_masked": f"...{account_number[-4:]}" if account_number else "unknown",
            "type": acct.get("type", "UNKNOWN"),
            "positions": acct.get("positions", []),
            "current_balances": acct.get("currentBalances", {}),
        })
    return accounts
