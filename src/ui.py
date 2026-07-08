"""Shared design system: tokens, global CSS, plotly template, formatters.

One place for every visual decision so all views read as a single product.
Styled to Linear's design language (docs/linear.DESIGN.md): near-black canvas
(#010102), surface ladder with hairline borders, ONE chromatic accent — Linear
lavender #5E6AD2 — used scarcely. Inter is the spec's sanctioned substitute for
the proprietary Linear typeface. Green/red stay for P&L semantics (the spec's
Known Gaps note: Linear's product UI itself uses a richer semantic palette).
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- Design tokens (Linear: docs/linear.DESIGN.md) -------------------------------
BG = "#010102"             # canvas — near-black with faint blue tint (never #000)
SURFACE = "#0F1011"        # surface-1: cards, tables, sidebar
SURFACE_2 = "#141516"      # surface-2: hover / nested / badges
BORDER = "#23252A"         # hairline
BORDER_STRONG = "#34343A"  # hairline-strong
TEXT = "#F7F8F8"           # ink
MUTED = "#8A8F98"          # ink-subtle
PRIMARY = "#5E6AD2"        # Linear lavender — THE accent; use scarcely
PRIMARY_LIGHT = "#828FFF"  # lavender hover — secondary series (SMA-50)
PRIMARY_MUTED = "#7A7FAD"  # brand-secure lavender-gray — tertiary series (SMA-200)
GREEN = "#27A644"          # semantic success (Linear's green) — gains
RED = "#E5484D"            # losses (desaturated to sit on the dark canvas)

COLORWAY = [PRIMARY, PRIMARY_LIGHT, PRIMARY_MUTED, GREEN, RED, "#D0D6E0", "#62666D"]

FONT_STACK = "'Inter', 'SF Pro Display', -apple-system, system-ui, 'Segoe UI', sans-serif"


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

/* Typography scale — Linear: display 600 with negative tracking, body 400 */
h1 {{
    font-size: 1.5rem !important; font-weight: 600 !important;
    letter-spacing: -0.02em; color: {TEXT} !important;
    padding-bottom: 0 !important;
}}
h2 {{
    /* Linear "eyebrow": small caps label with POSITIVE tracking, hairline rule */
    font-size: 0.74rem !important; font-weight: 500 !important;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: {MUTED} !important;
    border-bottom: 1px solid {BORDER}; padding-bottom: 0.45rem !important;
    margin-top: 0.9rem !important;
}}
h3 {{
    font-size: 1.05rem !important; font-weight: 500 !important;
    letter-spacing: -0.01em; color: {TEXT} !important;
}}

/* Metric cards — Linear feature-card: surface-1, hairline, 12px radius */
[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
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

/* Tables: tabular numerals, hairline border, 12px radius */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden;
}}
[data-testid="stDataFrame"] * {{
    font-variant-numeric: tabular-nums;
}}

/* Inputs — Linear text-input: surface-1, 8px radius, lavender focus ring */
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb] {{
    font-size: 0.88rem;
}}
[data-testid="stTextInput"] > div > div, [data-testid="stSelectbox"] > div > div {{
    background: {SURFACE} !important; border-radius: 8px;
}}
[data-testid="stTextInput"] > div > div:focus-within {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 2px rgba(94, 106, 210, 0.5) !important;
}}

/* Buttons — Linear button-secondary: surface-1, hairline, 8px radius */
[data-testid="stBaseButton-secondary"] {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;
    color: {TEXT}; font-weight: 500; font-size: 0.85rem;
}}
[data-testid="stBaseButton-secondary"]:hover {{
    background: {SURFACE_2}; border-color: {BORDER_STRONG}; color: {TEXT};
}}

/* Sidebar nav: active item = surface lift; lavender reserved for the active icon */
[data-testid="stSidebarNav"] a {{
    border-radius: 8px;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background: {SURFACE_2} !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] [data-testid="stIconMaterial"] {{
    color: {PRIMARY} !important;
}}

/* Captions and dividers */
[data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
hr {{ border-color: {BORDER} !important; }}

/* News cards — Linear feature-card, hover = surface-2 lift */
.pl-news-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 0.85rem 1.05rem; margin-bottom: 0.6rem;
    transition: background 150ms ease, border-color 150ms ease;
}}
.pl-news-card:hover {{ background: {SURFACE_2}; border-color: {BORDER_STRONG}; }}
.pl-news-card a {{
    color: {TEXT}; font-weight: 500; font-size: 0.93rem; text-decoration: none;
    line-height: 1.35; letter-spacing: -0.005em;
}}
.pl-news-card a:hover {{ color: {PRIMARY_LIGHT}; }}
.pl-news-summary {{
    color: {MUTED}; font-size: 0.82rem; line-height: 1.5; margin: 0.3rem 0 0.35rem 0;
}}
.pl-news-meta {{ color: {MUTED}; font-size: 0.72rem; }}
.pl-ticker-badge {{
    /* Linear status-badge: surface-2 pill, muted ink */
    display: inline-block; background: {SURFACE_2}; border: 1px solid {BORDER};
    color: #D0D6E0; font-size: 0.68rem; font-weight: 500; letter-spacing: 0.04em;
    padding: 0.1rem 0.55rem; border-radius: 9999px; margin-right: 0.5rem;
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
