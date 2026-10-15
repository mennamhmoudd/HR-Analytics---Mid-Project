import streamlit as st
from theme import apply_app_theme

st.set_page_config(
    page_title="HR Analytics | Mid Project",
    page_icon=":material/analytics:",
    layout="wide",
)

# ---- Shared visual styling (logo palette: tan / black / white) ----
apply_app_theme(show_toggle=True)

# ---- Company logo ----
st.logo(r"/Users/menna/Python/EDA/Final Project/Code/IMG_1343.png", size="large")

st.sidebar.markdown("### HR Analytics")
st.sidebar.caption("HR · People · Performance · Insights")

# ---- Payroll pages ----
payroll_dashboard = st.Page(
    r"/Users/menna/Python/EDA/Final Project/Code/pages/Payroll.py",
    title="Payroll Dashboard",
    icon=":material/dashboard:",
    default=True,
)

voice_assistant = st.Page(
    r"/Users/menna/Python/EDA/Final Project/Code/pages/Voice Assistant.py",
    title="AI Assistant",
    icon=":material/smart_toy:",
)

# ---- Recruitment pages ----
recruitment_dashboard = st.Page(
    r"/Users/menna/Python/EDA/Final Project/Code/pages/Recruitment Dashboard.py",
    title="Recruitment Dashboard",
    icon=":material/dashboard:",
)

# NOTE: the original path had no ".py" extension, which makes st.Page fail.
recruitment_reports = st.Page(
    r"/Users/menna/Python/EDA/Final Project/Code/pages/Recruitment Reports.py",
    title="Recruitment Reports",
    icon=":material/assessment:",
)

# ---- Navigation structure ----
pages = {
    "Payroll": [payroll_dashboard, voice_assistant],
    "Recruitment": [recruitment_dashboard, recruitment_reports],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
