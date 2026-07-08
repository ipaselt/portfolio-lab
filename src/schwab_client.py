"""Schwab Trader API client — read-only. Never places, modifies, or cancels orders.

Reads positions and balances across EVERY account this token's OAuth consent covers, unlike
trade-log's client, which only ever looks at accounts[0] (fine there — it only cares about one
account's option trades).

Field names verified against a live response 2026-07-08. Gotchas learned from real data:
- `securitiesAccount.type` is CASH vs MARGIN, NOT the account category — nothing in the response
  says "Roth IRA" vs "Individual". Human-readable names come from ACCOUNT_LABELS in .env.
- An account with no positions has NO `positions` key at all (not an empty list).
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


def _account_labels():
    """Parse ACCOUNT_LABELS from .env: '1234:Individual,5678:Roth IRA' → {last4: label}."""
    raw = os.environ.get("ACCOUNT_LABELS", "")
    labels = {}
    for pair in raw.split(","):
        if ":" in pair:
            last4, label = pair.split(":", 1)
            labels[last4.strip()] = label.strip()
    return labels


def get_accounts_summary(client):
    """Return every account this token can see: label, masked number, positions, balances."""
    resp = client.get_accounts(fields=[client.Account.Fields.POSITIONS])
    resp.raise_for_status()

    labels = _account_labels()
    accounts = []
    for entry in resp.json():
        acct = entry["securitiesAccount"]
        account_number = acct.get("accountNumber", "")
        last4 = account_number[-4:] if account_number else ""
        accounts.append({
            "account_number_masked": f"...{last4}" if last4 else "unknown",
            "label": labels.get(last4, f"...{last4}" if last4 else "unknown"),
            "type": acct.get("type", "UNKNOWN"),
            "positions": acct.get("positions", []),
            "current_balances": acct.get("currentBalances", {}),
            "liquidation_value": acct.get("currentBalances", {}).get("liquidationValue", 0.0),
        })
    return accounts
