"""Aggregate Schwab account/position data into a portfolio view.

UNVERIFIED field names (see schwab_client.py docstring) — the position dict is assumed to look like
schwab-py's documented shape (`instrument.symbol`, `longQuantity`, `averagePrice`, `marketValue`,
`longOpenProfitLoss`). Fix `_flatten_position` once real data is in hand (planning/todo.md #2/#4).
"""
import pandas as pd
import plotly.express as px


def _flatten_position(account, position):
    instrument = position.get("instrument", {})
    quantity = position.get("longQuantity", 0) or -position.get("shortQuantity", 0)
    market_value = position.get("marketValue", 0.0)
    unrealized_pl = position.get("longOpenProfitLoss", 0.0)
    average_price = position.get("averagePrice", 0.0)
    return {
        "account_type": account["type"],
        "account_masked": account["account_number_masked"],
        "symbol": instrument.get("symbol", "UNKNOWN"),
        "quantity": quantity,
        "average_price": average_price,
        "market_value": market_value,
        "unrealized_pl": unrealized_pl,
        "unrealized_pl_pct": (unrealized_pl / market_value * 100) if market_value else 0.0,
    }


def positions_dataframe(accounts):
    """Flatten every account's positions into one DataFrame, one row per position."""
    rows = [
        _flatten_position(account, position)
        for account in accounts
        for position in account["positions"]
    ]
    return pd.DataFrame(rows, columns=[
        "account_type", "account_masked", "symbol", "quantity",
        "average_price", "market_value", "unrealized_pl", "unrealized_pl_pct",
    ])


def allocation_by_symbol(df):
    """Return a plotly pie chart of portfolio allocation by symbol (summed across accounts)."""
    by_symbol = df.groupby("symbol", as_index=False)["market_value"].sum()
    return px.pie(by_symbol, names="symbol", values="market_value", title="Allocation by symbol")


def total_unrealized_pl(df):
    """Return (total unrealized $ P&L, total market value, blended % P&L)."""
    total_pl = df["unrealized_pl"].sum()
    total_value = df["market_value"].sum()
    pct = (total_pl / (total_value - total_pl) * 100) if (total_value - total_pl) else 0.0
    return total_pl, total_value, pct
