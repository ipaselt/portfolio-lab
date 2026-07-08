"""Tests for portfolio.py aggregation logic against a synthetic accounts-summary fixture.

This validates the aggregation math against the ASSUMED Schwab response shape — it does not
validate that Schwab's real API actually returns this shape (see schwab_client.py docstring).
"""
from src.portfolio import (
    account_performance,
    allocation_by_symbol,
    positions_dataframe,
    total_unrealized_pl,
)

ACCOUNTS = [
    {
        "type": "CASH",
        "label": "Roth IRA",
        "account_number_masked": "...1111",
        "positions": [
            {
                "instrument": {"symbol": "VTI"},
                "longQuantity": 10,
                "averagePrice": 200.0,
                "marketValue": 2200.0,
                "longOpenProfitLoss": 200.0,
            },
        ],
        "current_balances": {},
    },
    {
        "type": "CASH",
        "label": "Individual",
        "account_number_masked": "...2222",
        "positions": [
            {
                "instrument": {"symbol": "VTI"},
                "longQuantity": 5,
                "averagePrice": 210.0,
                "marketValue": 1100.0,
                "longOpenProfitLoss": 50.0,
            },
            {
                "instrument": {"symbol": "AAPL"},
                "longQuantity": 2,
                "averagePrice": 150.0,
                "marketValue": 300.0,
                "longOpenProfitLoss": -20.0,
            },
        ],
        "current_balances": {},
    },
]


def test_positions_dataframe_flattens_all_accounts():
    df = positions_dataframe(ACCOUNTS)
    assert len(df) == 3
    assert set(df["symbol"]) == {"VTI", "AAPL"}
    assert set(df["account"]) == {"Roth IRA", "Individual"}


def test_unrealized_pl_pct_is_relative_to_cost_basis():
    df = positions_dataframe(ACCOUNTS)
    vti_roth = df[(df["symbol"] == "VTI") & (df["account"] == "Roth IRA")].iloc[0]
    # cost basis = 2200 - 200 = 2000 → +200 is +10%, not 200/2200=9.09%
    assert round(vti_roth["unrealized_pl_pct"], 2) == 10.0


def test_total_unrealized_pl_sums_across_accounts():
    df = positions_dataframe(ACCOUNTS)
    total_pl, total_value, pct = total_unrealized_pl(df)
    assert total_pl == 230.0
    assert total_value == 3600.0


def test_account_performance_rollup():
    df = positions_dataframe(ACCOUNTS)
    perf = account_performance(df)
    assert len(perf) == 2
    roth = perf[perf["account"] == "Roth IRA"].iloc[0]
    assert roth["market_value"] == 2200.0
    assert roth["cost_basis"] == 2000.0
    assert round(roth["unrealized_pl_pct"], 2) == 10.0
    # % of portfolio sums to 100
    assert round(perf["pct_of_portfolio"].sum(), 6) == 100.0


def test_pct_of_portfolio_column_sums_to_100():
    df = positions_dataframe(ACCOUNTS)
    assert round(df["pct_of_portfolio"].sum(), 6) == 100.0


def test_allocation_by_symbol_groups_across_accounts():
    df = positions_dataframe(ACCOUNTS)
    fig = allocation_by_symbol(df)
    # VTI appears in both accounts and should be summed into one bar, not two.
    symbols = list(fig.data[0].y)
    assert sorted(symbols) == ["AAPL", "VTI"]
    values = dict(zip(fig.data[0].y, fig.data[0].x))
    assert values["VTI"] == 3300.0  # 2200 + 1100 across the two accounts
