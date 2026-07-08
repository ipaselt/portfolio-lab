"""Shared design system: tokens, global CSS, plotly template, formatters.

One place for every visual decision so all views read as a single product.
Palette: institutional dark (deep navy surfaces, blue data, semantic green/red,
amber reserved for highlights). Typography: Inter, tabular numerals for data.
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- Design tokens -------------------------------------------------------------
BG = "#0B0F17"          # app background
SURFACE = "#111722"     # cards, tables, sidebar
SURFACE_2 = "#161D2A"   # hover / nested surfaces
BORDER = "#212B3B"
TEXT = "#E8ECF3"
MUTED = "#8A94A6"
BLUE = "#4F8EF7"        # primary data color
GREEN = "#22C55E"       # gains
RED = "#EF4444"         # losses
AMBER = "#E5A50A"       # highlight (SMA-50, callouts)
VIOLET = "#8B5CF6"      # secondary series (SMA-200)

COLORWAY = [BLUE, AMBER, VIOLET, GREEN, RED, "#38BDF8", "#F472B6", "#A3E635"]

FONT_STACK = "'Inter', -apple-system, 'Segoe UI', sans-serif"


def inject_css():
    """Global stylesheet — call once per page render, right after set_page_config."""
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="st-"] {{
    font-family: {FONT_STACK};
}}
/* The global font rule above must NOT clobber Material Symbols icons */
[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded' !important;
}}

/* Hide Streamlit chrome: deploy button, main menu, colored decoration bar */
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{
    display: none !important;
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* App shell */
.stApp {{ background: {BG}; }}
.block-container {{ padding-top: 2.2rem; max-width: 1240px; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebarNav"] a span, [data-testid="stSidebar"] span {{
    font-size: 0.86rem;
}}

/* Typography scale */
h1 {{
    font-size: 1.45rem !important; font-weight: 650 !important;
    letter-spacing: -0.01em; color: {TEXT} !important;
    padding-bottom: 0 !important;
}}
h2 {{
    font-size: 0.78rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: {MUTED} !important;
    border-bottom: 1px solid {BORDER}; padding-bottom: 0.45rem !important;
    margin-top: 0.8rem !important;
}}
h3 {{
    font-size: 1.02rem !important; font-weight: 600 !important; color: {TEXT} !important;
}}

/* Metric cards */
[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
}}
[data-testid="stMetricLabel"] {{ white-space: normal !important; }}
[data-testid="stMetricLabel"] p {{
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.08em; color: {MUTED} !important;
    white-space: normal !important;
}}
[data-testid="stMetricValue"] {{
    font-size: clamp(1.02rem, 1.35vw, 1.32rem) !important; font-weight: 600 !important;
    font-variant-numeric: tabular-nums; color: {TEXT} !important;
}}
/* Never ellipsize a dollar figure — the full number is the whole point */
[data-testid="stMetricValue"] > div {{
    overflow: visible !important; text-overflow: clip !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important; font-variant-numeric: tabular-nums;
}}

/* Tables: tabular numerals, tighter, bordered */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER}; border-radius: 10px; overflow: hidden;
}}
[data-testid="stDataFrame"] * {{
    font-variant-numeric: tabular-nums;
}}

/* Inputs */
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb] {{
    font-size: 0.88rem;
}}

/* Captions and dividers */
[data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
hr {{ border-color: {BORDER} !important; }}

/* News cards */
.pl-news-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 0.85rem 1.05rem; margin-bottom: 0.6rem;
}}
.pl-news-card a {{
    color: {TEXT}; font-weight: 600; font-size: 0.93rem; text-decoration: none;
    line-height: 1.35;
}}
.pl-news-card a:hover {{ color: {BLUE}; }}
.pl-news-summary {{
    color: {MUTED}; font-size: 0.82rem; line-height: 1.5; margin: 0.3rem 0 0.35rem 0;
}}
.pl-news-meta {{ color: {MUTED}; font-size: 0.72rem; }}
.pl-ticker-badge {{
    display: inline-block; background: {SURFACE_2}; border: 1px solid {BORDER};
    color: {BLUE}; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.04em;
    padding: 0.1rem 0.45rem; border-radius: 5px; margin-right: 0.5rem;
    font-variant-numeric: tabular-nums; vertical-align: 2px;
}}
.pl-asof {{
    color: {MUTED}; font-size: 0.74rem; letter-spacing: 0.02em;
    font-variant-numeric: tabular-nums;
}}
</style>""", unsafe_allow_html=True)


def register_plotly_template():
    """Register + set the app-wide plotly template. Call once per page render."""
    if "portfolio_lab" not in pio.templates:
        pio.templates["portfolio_lab"] = go.layout.Template(layout=dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_STACK.replace("'", ""), color=TEXT, size=12),
            colorway=COLORWAY,
            xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER,
                       tickfont=dict(color=MUTED, size=11)),
            yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER,
                       tickfont=dict(color=MUTED, size=11)),
            legend=dict(font=dict(color=MUTED, size=11), bgcolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=BORDER,
                            font=dict(family=FONT_STACK.replace("'", ""), color=TEXT, size=12)),
            margin=dict(l=48, r=16, t=44, b=40),
            title=dict(font=dict(size=13, color=MUTED)),
        ))
    pio.templates.default = "portfolio_lab"


def page_header(title, subtitle=None):
    """Consistent page header: title + muted subtitle/as-of line."""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f'<div class="pl-asof">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown("")


def signed_usd(value):
    """-1234.5 → '-$1,234.50' · 1234.5 → '+$1,234.50' (explicit sign for P&L)."""
    sign = "-" if value < 0 else "+"
    return f"{sign}${abs(value):,.2f}"


def signed_pct(value):
    sign = "-" if value < 0 else "+"
    return f"{sign}{abs(value):,.2f}%"
