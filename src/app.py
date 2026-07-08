"""Portfolio Lab — app entrypoint. Run: streamlit run src/app.py

Anchors itself to the project root so relative .env / token / data paths resolve from any cwd,
then hands off to st.navigation. All views share the design system in src/ui.py.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.ui import inject_css, register_plotly_template

st.set_page_config(
    page_title="Portfolio Lab",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
register_plotly_template()

nav = st.navigation([
    st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("views/research.py", title="Research", icon=":material/query_stats:"),
    st.Page("views/charts.py", title="Charts", icon=":material/candlestick_chart:"),
    st.Page("views/news.py", title="News", icon=":material/newspaper:"),
])
nav.run()
