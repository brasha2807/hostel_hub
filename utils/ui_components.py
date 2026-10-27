import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px


def inject_custom_css(bg_clarity="Vivid (Recommended)", bg_image_uri=""):
    """
    Injects an Awwwards-level modern design system into the Streamlit application.
    Features: Google Fonts (Plus Jakarta Sans & Outfit), glassmorphism, glowing borders,
    micro-animations, modern scrollbars, and customized Streamlit widgets.
    """
    # Dynamic opacity presets based on user's clarity preference
    if bg_clarity == "Crystal Clear":
        overlay = "rgba(8, 13, 26, 0.48)"
        card_bg = "rgba(15, 23, 42, 0.82)"
        card_border = "rgba(255, 255, 255, 0.18)"
        blur_val = "16px"
    elif bg_clarity == "Vivid (Recommended)":
        overlay = "rgba(8, 13, 26, 0.72)"
        card_bg = "rgba(15, 23, 42, 0.88)"
        card_border = "rgba(255, 255, 255, 0.15)"
        blur_val = "20px"
    elif bg_clarity == "Soft Tint":
        overlay = "rgba(8, 13, 26, 0.85)"
        card_bg = "rgba(15, 23, 42, 0.92)"
        card_border = "rgba(255, 255, 255, 0.10)"
        blur_val = "14px"
    else:  # Muted
        overlay = "rgba(8, 13, 26, 0.95)"
        card_bg = "rgba(15, 23, 42, 0.96)"
        card_border = "rgba(255, 255, 255, 0.08)"
        blur_val = "10px"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {{
        --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-heading: 'Outfit', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --bg-deep: #080D1A;
        --primary-glow: #00F5D4;
        --accent-cyan: #38BDF8;
        --accent-indigo: #6366F1;
        --card-bg: {card_bg};
        --card-border: {card_border};
        --card-blur: {blur_val};
        --text-pure: #F8FAFC;
        --text-sub: #CBD5E1;
        --text-muted: #94A3B8;
    }}

    html, body, [class*="css"] {{
        font-family: var(--font-main);
        color: var(--text-pure) !important;
    }}

    /* STREAMLIT TOP HEADER FIX: REMOVE GLARING WHITE BAR */
    header[data-testid="stHeader"],
    .stApp > header {{
        background: rgba(8, 13, 26, 0.80) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }}

    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] button {{
        color: #F8FAFC !important;
        fill: #F8FAFC !important;
    }}

    /* HEADINGS: ALWAYS PURE VIVID WHITE WITH CRISP CONTRAST */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6 {{
        font-family: var(--font-heading) !important;
        letter-spacing: -0.02em;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.6) !important;
    }}

    /* BODY PARAGRAPHS & LABELS */
    p, span, label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {{
        color: #E2E8F0 !important;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .stCaption {{
        color: #94A3B8 !important;
        font-size: 13px !important;
    }}

    /* GLOBAL APP BACKGROUND WITH FROSTED LUXURY ATMOSPHERE */
    .stApp {{
        background: linear-gradient({overlay}, {overlay}), url("{bg_image_uri}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }}

    .block-container {{
        max-width: 1480px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }}

    /* SLEEK DARK GLASS SIDEBAR */
    [data-testid="stSidebar"] {{
        background: rgba(8, 13, 26, 0.94) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 14px 0 !important;
    }}

    /* SIDEBAR SELECTBOX / NAVIGATION */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background: rgba(15, 23, 42, 0.90) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: var(--primary-glow) !important;
        box-shadow: 0 0 16px rgba(0, 245, 212, 0.2) !important;
    }}

    /* DROPDOWN POPOVER OPTIONS */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {{
        background: #0B132B !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6) !important;
    }}

    li[role="option"] {{
        background: transparent !important;
        color: #F8FAFC !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }}

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.2), rgba(99, 102, 241, 0.25)) !important;
        color: #FFFFFF !important;
    }}

    /* GLASSMORPHIC CONTAINERS & EXPANDERS */
    [data-testid="stExpander"],
    [data-testid="stForm"],
    .glass-panel {{
        background: var(--card-bg) !important;
        backdrop-filter: blur(var(--card-blur)) !important;
        -webkit-backdrop-filter: blur(var(--card-blur)) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 18px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }}

    [data-testid="stExpander"] details summary {{
        color: #F8FAFC !important;
        font-weight: 700 !important;
        background: rgba(15, 23, 42, 0.65) !important;
        border-radius: 14px !important;
    }}

    [data-testid="stExpander"] details summary p,
    [data-testid="stExpander"] details summary span {{
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }}

    [data-testid="stExpander"] details summary svg {{
        fill: #38BDF8 !important;
    }}

    /* AWWWARDS EXECUTIVE HERO BANNER */
    .aww-hero {{
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        padding: 42px 46px;
        margin-bottom: 28px;
        border: 1px solid rgba(255, 255, 255, 0.20);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }}

    .aww-hero::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 245, 212, 0.08) 0%, transparent 60%);
        pointer-events: none;
    }}

    .aww-hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(0, 245, 212, 0.4);
        color: #00F5D4;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }}

    /* STAT CARD TILES */
    .stat-tile {{
        background: var(--card-bg);
        backdrop-filter: blur(var(--card-blur));
        border: 1px solid var(--card-border);
        border-radius: 18px;
        padding: 22px 20px;
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }}

    .stat-tile:hover {{
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35), 0 0 20px rgba(56, 189, 248, 0.15);
    }}

    .stat-tile-label {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-sub);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .stat-tile-value {{
        font-family: var(--font-heading);
        font-size: 34px;
        font-weight: 850;
        color: var(--text-pure);
        margin: 6px 0 4px 0;
        letter-spacing: -0.02em;
    }}

    .stat-tile-sub {{
        font-size: 12px;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    /* BUTTONS */
    .stButton > button,
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        font-family: var(--font-main) !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        padding: 0.6rem 1.4rem !important;
        min-height: 44px !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
        box-shadow: 0 8px 24px rgba(14, 165, 233, 0.5) !important;
        transform: translateY(-2px) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
    }}

    /* PRIMARY CTA BUTTONS */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }}

    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #10B981 0%, #34D399 100%) !important;
        box-shadow: 0 10px 28px rgba(16, 185, 129, 0.6) !important;
    }}

    /* INPUTS & TEXT AREAS */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stTextArea"] textarea {{
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        font-family: var(--font-main) !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stDateInput"] input:focus,
    [data-testid="stTimeInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {{
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
        background: rgba(15, 23, 42, 0.95) !important;
    }}

    /* BADGES & CHIPS */
    .pill-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .pill-success {{
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }}

    .pill-warning {{
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }}

    .pill-info {{
        background: rgba(56, 189, 248, 0.15);
        color: #7DD3FC;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }}

    .pill-neutral {{
        background: rgba(148, 163, 184, 0.15);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.35);
    }}

    /* PULSING RADAR DOT */
    .radar-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: radar-pulse 1.8s infinite cubic-bezier(0.66, 0, 0, 1);
        margin-right: 6px;
    }}

    @keyframes radar-pulse {{
        to {{
            box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_plotly_dark_theme():
    """Returns standard Plotly layout configuration tailored to the dark luxury glass aesthetic."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#E2E8F0"),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(color="#94A3B8"),
            linecolor="rgba(255, 255, 255, 0.1)"
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(color="#94A3B8"),
            linecolor="rgba(255, 255, 255, 0.1)"
        )
    )
