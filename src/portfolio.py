"""Aggregate Schwab account/position data into a portfolio view.

Position field names (`instrument.symbol`, `longQuantity`, `averagePrice`, `marketValue`,
`longOpenProfitLoss`) verified against a live Schwab response 2026-07-08.
"""
import pandas as pd
import plotly.graph_objects as go

from src.ui import GREEN, MUTED, PRIMARY, RED


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
    """Bar chart of unrealized P&L per account, semantic green/red by sign."""
    perf = account_performance(df)
    colors = [GREEN if v >= 0 else RED for v in perf["unrealized_pl"]]
    fig = go.Figure(go.Bar(
        x=perf["account"], y=perf["unrealized_pl"], marker=dict(color=colors),
        text=[f"{'+' if v >= 0 else '-'}${abs(v):,.0f}" for v in perf["unrealized_pl"]],
        textposition="outside", textfont=dict(size=11, color=MUTED),
        hovertemplate="%{x}: $%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        title="UNREALIZED P&L BY ACCOUNT", height=300, showlegend=False, bargap=0.55,
        yaxis=dict(title=None, tickprefix="$", tickformat=",.0f"), xaxis=dict(title=None),
    )
    return fig


def allocation_by_symbol(df):
    """Horizontal bar of allocation by symbol, largest first — reads more precisely than a pie."""
    by_symbol = (df.groupby("symbol", as_index=False)["market_value"].sum()
                 .sort_values("market_value", ascending=True))
    total = by_symbol["market_value"].sum()
    pct = by_symbol["market_value"] / total * 100 if total else by_symbol["market_value"] * 0
    fig = go.Figure(go.Bar(
        x=by_symbol["market_value"], y=by_symbol["symbol"], orientation="h",
        marker=dict(color=PRIMARY), text=[f"{p:.1f}%" for p in pct],
        textposition="outside", textfont=dict(size=11, color=MUTED),
        hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title="ALLOCATION BY SYMBOL", height=max(260, 34 * len(by_symbol) + 90),
        xaxis=dict(title=None, tickprefix="$", tickformat=",.0f"),
        yaxis=dict(title=None), showlegend=False, bargap=0.35,
        xaxis_range=[0, by_symbol["market_value"].max() * 1.18],
    )
    return fig


def total_unrealized_pl(df):
    """Return (total unrealized $ P&L, total market value, blended % P&L)."""
    total_pl = df["unrealized_pl"].sum()
    total_value = df["market_value"].sum()
    pct = (total_pl / (total_value - total_pl) * 100) if (total_value - total_pl) else 0.0
    return total_pl, total_value, pct
