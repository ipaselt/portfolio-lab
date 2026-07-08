"""Aggregate Schwab account/position data into a portfolio view.

Position field names (`instrument.symbol`, `longQuantity`, `averagePrice`, `marketValue`,
`longOpenProfitLoss`) verified against a live Schwab response 2026-07-08.
"""
import pandas as pd
import plotly.express as px


def _flatten_position(account, position):
    instrument = position.get("instrument", {})
    quantity = position.get("longQuantity", 0) or -position.get("shortQuantity", 0)
    market_value = position.get("marketValue", 0.0)
    unrealized_pl = position.get("longOpenProfitLoss", 0.0)
    average_price = position.get("averagePrice", 0.0)
    cost_basis = market_value - unrealized_pl
    return {
        "account": account["label"],
        "account_masked": account["account_number_masked"],
        "symbol": instrument.get("symbol", "UNKNOWN"),
        "quantity": quantity,
        "average_price": average_price,
        "market_value": market_value,
        "unrealized_pl": unrealized_pl,
        "unrealized_pl_pct": (unrealized_pl / cost_basis * 100) if cost_basis else 0.0,
    }


def positions_dataframe(accounts):
    """Flatten every account's positions into one DataFrame, one row per position."""
    rows = [
        _flatten_position(account, position)
        for account in accounts
        for position in account["positions"]
    ]
    df = pd.DataFrame(rows, columns=[
        "account", "account_masked", "symbol", "quantity",
        "average_price", "market_value", "unrealized_pl", "unrealized_pl_pct",
    ])
    total_value = df["market_value"].sum()
    df["pct_of_portfolio"] = (df["market_value"] / total_value * 100) if total_value else 0.0
    return df


def account_performance(df):
    """Per-account rollup: market value, cost basis, unrealized P&L ($ and %), % of portfolio."""
    grouped = df.groupby("account").agg(
        market_value=("market_value", "sum"),
        unrealized_pl=("unrealized_pl", "sum"),
        positions=("symbol", "count"),
    ).reset_index()
    grouped["cost_basis"] = grouped["market_value"] - grouped["unrealized_pl"]
    grouped["unrealized_pl_pct"] = grouped.apply(
        lambda r: (r["unrealized_pl"] / r["cost_basis"] * 100) if r["cost_basis"] else 0.0, axis=1)
    total_value = grouped["market_value"].sum()
    grouped["pct_of_portfolio"] = (grouped["market_value"] / total_value * 100) if total_value else 0.0
    return grouped[["account", "positions", "market_value", "cost_basis",
                    "unrealized_pl", "unrealized_pl_pct", "pct_of_portfolio"]]


def pl_by_account_chart(df):
    """Bar chart of unrealized P&L per account, green/red by sign."""
    perf = account_performance(df)
    fig = px.bar(perf, x="account", y="unrealized_pl", title="Unrealized P&L by account",
                 color=perf["unrealized_pl"] > 0,
                 color_discrete_map={True: "#2ca02c", False: "#d62728"})
    fig.update_layout(showlegend=False, yaxis_title="Unrealized P&L ($)", xaxis_title="")
    return fig


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
