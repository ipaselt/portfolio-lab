"""Tests for portfolio.py aggregation logic against a synthetic accounts-summary fixture.

This validates the aggregation math against the ASSUMED Schwab response shape — it does not
validate that Schwab's real API actually returns this shape (see schwab_client.py docstring).
"""
from src.portfolio import allocation_by_symbol, positions_dataframe, total_unrealized_pl

ACCOUNTS = [
    {
        "type": "ROTH IRA",
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
        "type": "INDIVIDUAL",
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
    assert set(df["account_type"]) == {"ROTH IRA", "INDIVIDUAL"}


def test_total_unrealized_pl_sums_across_accounts():
    df = positions_dataframe(ACCOUNTS)
    total_pl, total_value, pct = total_unrealized_pl(df)
    assert total_pl == 230.0
    assert total_value == 3600.0


def test_allocation_by_symbol_groups_across_accounts():
    df = positions_dataframe(ACCOUNTS)
    fig = allocation_by_symbol(df)
    # VTI appears in both accounts and should be summed into one slice, not two.
    labels = list(fig.data[0].labels)
    assert sorted(labels) == ["AAPL", "VTI"]
