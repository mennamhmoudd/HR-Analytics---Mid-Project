"""Shared visual theme for the HR Analytics Streamlit app (Misr Beni Suef HR).

Palette is taken from the company logo: tan/gold, black and white.
This module changes presentation only. It does not transform or modify datasets.
"""
import streamlit as st

LIGHT_COLORS = {
    "primary": "#111111",      # logo black
    "accent": "#A38B5F",       # logo tan
    "accent_dark": "#7D6A45",
    "accent_soft": "#F3EEE4",  # light tan tint
    "bg": "#FAF8F4",
    "surface": "#FFFFFF",
    "text": "#1C1C1C",
    "secondary": "#6B6459",
    "border": "#E6DFD0",
    "grid": "#EFE9DC",
    "chart": ["#A38B5F", "#111111", "#7D6A45", "#CDBB94", "#4A4A4A", "#B5651D"],
}

DARK_COLORS = {
    "primary": "#D4BE92",      # light tan for headings on black
    "accent": "#A38B5F",
    "accent_dark": "#C4A97A",
    "accent_soft": "#262219",
    "bg": "#0B0B0B",
    "surface": "#161616",
    "text": "#EFEAE0",
    "secondary": "#A39B8B",
    "border": "#2C2A25",
    "grid": "#2C2A25",
    "chart": ["#A38B5F", "#F2EDE3", "#D4BE92", "#6B6459", "#E0A96D", "#8A8A8A"],
}


def is_dark_mode():
    """Prefer the app's toggle, falling back to Streamlit's configured theme."""
    if "hr_dark_mode" in st.session_state:
        return bool(st.session_state["hr_dark_mode"])
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def get_colors():
    return DARK_COLORS if is_dark_mode() else LIGHT_COLORS


def apply_app_theme(show_toggle=False):
    """Apply consistent, responsive CSS to the current Streamlit page."""
    if show_toggle:
        st.sidebar.toggle("Dark mode", key="hr_dark_mode")

    c = get_colors()
    st.markdown(
        f"""
        <style>
        :root {{
          --hr-primary: {c['primary']}; --hr-accent: {c['accent']};
          --hr-accent-dark: {c['accent_dark']}; --hr-soft: {c['accent_soft']};
          --hr-bg: {c['bg']}; --hr-surface: {c['surface']};
          --hr-text: {c['text']}; --hr-secondary: {c['secondary']};
          --hr-border: {c['border']};
        }}

        /* ---------- Base ---------- */
        .stApp {{ background: var(--hr-bg); color: var(--hr-text); }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stAppViewContainer"] > .main {{ background: var(--hr-bg); }}
        [data-testid="stMainBlockContainer"] {{
          padding-top: 1.65rem; padding-bottom: 2.5rem; max-width: 1600px;
        }}
        h1, h2, h3, h4, h5 {{ color: var(--hr-primary) !important; letter-spacing: -0.02em; }}
        h1 {{ font-weight: 800 !important; }}
        h2, h3 {{ font-weight: 700 !important; }}
        h5 {{ text-transform: uppercase; letter-spacing: .08em; font-size: .78rem !important;
              color: var(--hr-accent-dark) !important; }}
        p, label, [data-testid="stMetricLabel"] {{ color: var(--hr-text); }}
        [data-testid="stCaptionContainer"] {{ color: var(--hr-secondary); }}

        /* Page title gets a tan underline accent */
        h1::after {{
          content: ""; display: block; width: 64px; height: 4px; margin-top: .45rem;
          background: var(--hr-accent); border-radius: 2px;
        }}
        hr {{ border-color: var(--hr-border); }}

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {{
          background: var(--hr-surface); border-right: 1px solid var(--hr-border);
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: var(--hr-secondary); }}
        [data-testid="stSidebar"] [data-testid="stLogo"] img {{
          width: 150px !important; max-width: 100% !important; height: auto !important;
          object-fit: contain;
        }}
        [data-testid="stSidebar"] [data-testid="stLogo"] {{
          width: 100%; padding: 14px 8px 18px 8px;
        }}
        [data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"] {{
          border-radius: 10px; margin: 2px 0; font-weight: 600;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
          background: var(--hr-soft) !important;
          border-left: 4px solid var(--hr-accent);
          color: var(--hr-primary) !important;
        }}
        [data-testid="stSidebarNavSeparator"] {{ color: var(--hr-accent-dark); }}

        /* ---------- KPI cards ---------- */
        [data-testid="stMetric"] {{
          background: var(--hr-surface); border: 1px solid var(--hr-border);
          border-left: 5px solid var(--hr-accent);
          border-radius: 14px; padding: 0.55rem 1rem !important; min-height: 104px;
          box-shadow: 0 2px 10px rgba(17, 17, 17, 0.05);
          box-sizing: border-box !important;
          transition: box-shadow .15s ease, transform .15s ease;
          height: 80px;
  
        }}
        [data-testid="stMetric"]:hover {{
          box-shadow: 0 6px 18px rgba(163, 139, 95, 0.22); transform: translateY(-1px);
        }}
        [data-testid="stMetricLabel"] {{
          color: var(--hr-secondary) !important; font-weight: 200;
          text-transform: uppercase; letter-spacing: .03 rem; font-size: .5rem !important;
        }}
        [data-testid="stMetricValue"] {{
          color: var(--hr-primary) !important; font-size: 1.7rem ; font-weight: 800; line-height: 1.5 !important;
        }}
        [data-testid="stMetricDelta"] {{
          margin-top: -0.1rem !important; margin-bottom: 0 !important;
          line-height: .9 !important; font-size: 0.65rem !important;
          white-space: nowrap !important; overflow: visible !important;
        }}

        /* ---------- Tabs ---------- */
        [data-testid="stTabs"] [role="tablist"] {{
          gap: .35rem; border-bottom: 2px solid var(--hr-border);
        }}
        [data-testid="stTabs"] button[role="tab"] {{
          border-radius: 10px 10px 0 0; padding: .65rem 1rem;
          color: var(--hr-secondary); font-weight: 600;
        }}
        [data-testid="stTabs"] button[role="tab"]:hover {{
          background: var(--hr-soft); color: var(--hr-primary);
        }}
        [data-testid="stTabs"] button[aria-selected="true"] {{
          color: var(--hr-primary); background: var(--hr-soft);
          border-bottom: 3px solid var(--hr-accent);
        }}
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background-color: var(--hr-accent) !important; }}

        /* ---------- Tables & inputs ---------- */
        [data-testid="stDataFrame"], [data-testid="stTable"] {{
          border: 1px solid var(--hr-border); border-radius: 12px; overflow: hidden;
          box-shadow: 0 2px 10px rgba(17, 17, 17, 0.04);
        }}
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{
          border-radius: 10px !important; border-color: var(--hr-border) !important;
          background: var(--hr-surface) !important;
        }}
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within {{
          border-color: var(--hr-accent) !important;
          box-shadow: 0 0 0 2px rgba(163, 139, 95, .25) !important;
        }}

        /* ---------- Buttons ---------- */
        .stButton > button, [data-testid="stDownloadButton"] button {{
          border-radius: 10px; font-weight: 650; border: 1px solid var(--hr-border);
          background: var(--hr-surface); color: var(--hr-text);
          transition: all .15s ease;
        }}
        .stButton > button:hover, [data-testid="stDownloadButton"] button:hover {{
          border-color: var(--hr-accent); background: var(--hr-soft);
          color: var(--hr-primary); transform: translateY(-1px);
        }}
        .stButton > button[kind="primary"] {{
          background: var(--hr-accent); color: #fff; border-color: var(--hr-accent);
        }}

        /* ---------- Chat (AI assistant) ---------- */
        [data-testid="stChatMessage"] {{
          background: var(--hr-surface); border: 1px solid var(--hr-border);
          border-radius: 14px; padding: .9rem 1rem;
        }}
        [data-testid="stChatInput"] {{ border-color: var(--hr-accent) !important; }}

        /* ---------- Responsive ---------- */
        @media (max-width: 900px) {{
          [data-testid="stMainBlockContainer"] {{ padding: 1rem .8rem 2rem; }}
          [data-testid="stMetric"] {{ padding: .6rem .8rem !important; min-height: 90px; }}
        }}
        @media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_chart_theme(fig, title=None):
    """Apply shared chart styling without changing chart data or chart type."""
    c = get_colors()
    if title is not None:
        fig.update_layout(title_text=title)
    fig.update_layout(
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", color=c["text"], size=12),
        paper_bgcolor=c["surface"],
        plot_bgcolor=c["surface"],
        colorway=c["chart"],
        margin=dict(l=18, r=18, t=52, b=18),
        title=dict(font=dict(size=16, color=c["primary"]), x=0.02, xanchor="left"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=c["secondary"])),
        hoverlabel=dict(bgcolor=c["surface"], font_color=c["text"], bordercolor=c["accent"]),
    )
    fig.update_xaxes(
        gridcolor=c["grid"], linecolor=c["border"], zerolinecolor=c["grid"],
        tickfont=dict(color=c["secondary"]), title_font=dict(color=c["secondary"]),
    )
    fig.update_yaxes(
        gridcolor=c["grid"], linecolor=c["border"], zerolinecolor=c["grid"],
        tickfont=dict(color=c["secondary"]), title_font=dict(color=c["secondary"]),
    )
    return fig
