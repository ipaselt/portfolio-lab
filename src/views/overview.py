"""Overview — accounts, performance, positions, allocation."""
from datetime import datetime

import streamlit as st

from src.portfolio import (
    account_performance,
    allocation_by_symbol,
    pl_by_account_chart,
    positions_dataframe,
    total_unrealized_pl,
)
from src.schwab_client import ReauthNeeded, get_accounts_summary, get_client
from src.ui import page_header, signed_pct, signed_usd

try:
    client = get_client()
    accounts = get_accounts_summary(client)
except ReauthNeeded as e:
    st.error(f"{e}\n\nRun `python -m src.authenticate` in a terminal, then reload this page.")
    st.stop()
except KeyError:
    st.error("Missing SCHWAB_APP_KEY / SCHWAB_APP_SECRET — copy .env.example to .env and fill them in.")
    st.stop()

page_header(
    "Portfolio Overview",
    f"Schwab · {len(accounts)} accounts · as of {datetime.now():%b %d, %Y %H:%M} local",
)

df = positions_dataframe(accounts)
if df.empty:
    st.info("No positions found across the accounts this token can see.")
    st.stop()

# --- Headline metrics ----------------------------------------------------------
total_pl, total_value, pct = total_unrealized_pl(df)
account_value_total = sum(a["liquidation_value"] for a in accounts)
c1, c2, c3 = st.columns(3)
c1.metric("Total account value", f"${account_value_total:,.2f}",
          delta=f"{len(accounts)} accounts", delta_color="off")
c2.metric("Invested market value", f"${total_value:,.2f}")
c3.metric("Unrealized P&L", f"${total_pl:,.2f}", delta=signed_pct(pct))

# --- Accounts ------------------------------------------------------------------
st.markdown("## Accounts")
acct_cols = st.columns(len(accounts))
for col, acct in zip(acct_cols, accounts):
    col.metric(
        f"{acct['label']} ({acct['account_number_masked']})",
        f"${acct['liquidation_value']:,.2f}",
        delta=f"{len(acct['positions'])} positions",
        delta_color="off",
    )

# --- Performance by account -----------------------------------------------------
st.markdown("## Performance by Account")
perf = account_performance(df)
st.dataframe(
    perf,
    use_container_width=True, hide_index=True,
    column_config={
        "account": st.column_config.TextColumn("Account"),
        "positions": st.column_config.NumberColumn("Positions", format="%d"),
        "market_value": st.column_config.NumberColumn("Market Value", format="dollar"),
        "cost_basis": st.column_config.NumberColumn("Cost Basis", format="dollar"),
        "unrealized_pl": st.column_config.NumberColumn("Unrealized P&L", format="dollar"),
        "unrealized_pl_pct": st.column_config.NumberColumn("P&L %", format="%.2f%%"),
        "pct_of_portfolio": st.column_config.NumberColumn("% of Portfolio", format="%.1f%%"),
    },
)
st.plotly_chart(pl_by_account_chart(df), use_container_width=True)

# --- Positions -------------------------------------------------------------------
st.markdown("## Positions")
st.dataframe(
    df.sort_values("market_value", ascending=False),
    use_container_width=True, hide_index=True,
    column_config={
        "account": st.column_config.TextColumn("Account"),
        "account_masked": None,
        "symbol": st.column_config.TextColumn("Symbol"),
        "quantity": st.column_config.NumberColumn("Qty", format="%.2f"),
        "average_price": st.column_config.NumberColumn("Avg Price", format="dollar"),
        "market_value": st.column_config.NumberColumn("Market Value", format="dollar"),
        "unrealized_pl": st.column_config.NumberColumn("Unrealized P&L", format="dollar"),
        "unrealized_pl_pct": st.column_config.NumberColumn("P&L %", format="%.2f%%"),
        "pct_of_portfolio": st.column_config.NumberColumn("% of Portfolio", format="%.1f%%"),
    },
)

# --- Allocation -------------------------------------------------------------------
st.markdown("## Allocation")
st.plotly_chart(allocation_by_symbol(df), use_container_width=True)
