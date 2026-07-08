"""Portfolio Lab dashboard — local Streamlit app. Read-only against Schwab.

Run: streamlit run src/dashboard.py
"""
import streamlit as st

from src.schwab_client import ReauthNeeded, get_accounts_summary, get_client
from src.portfolio import allocation_by_symbol, positions_dataframe, total_unrealized_pl

st.set_page_config(page_title="Portfolio Lab", layout="wide")
st.title("Portfolio Lab")

try:
    client = get_client()
    accounts = get_accounts_summary(client)
except ReauthNeeded as e:
    st.error(f"{e}\n\nRun `python -m src.authenticate` in a terminal, then reload this page.")
    st.stop()
except KeyError:
    st.error("Missing SCHWAB_APP_KEY / SCHWAB_APP_SECRET — copy .env.example to .env and fill them in.")
    st.stop()

st.subheader("Accounts")
for acct in accounts:
    st.write(f"**{acct['type']}** ({acct['account_number_masked']}) — "
             f"{len(acct['positions'])} position(s)")

df = positions_dataframe(accounts)
if df.empty:
    st.info("No positions found across the accounts this token can see.")
else:
    total_pl, total_value, pct = total_unrealized_pl(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total market value", f"${total_value:,.2f}")
    col2.metric("Unrealized P&L", f"${total_pl:,.2f}")
    col3.metric("Unrealized P&L %", f"{pct:.2f}%")

    st.subheader("Positions")
    st.dataframe(df, use_container_width=True)

    st.subheader("Allocation by symbol")
    st.plotly_chart(allocation_by_symbol(df), use_container_width=True)
