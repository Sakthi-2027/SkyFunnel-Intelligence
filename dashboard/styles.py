import streamlit as st

CUSTOM_CSS = """
<style>
[data-testid="stMetric"] {
    background-color: #161B22;
    border: 1px solid #2A2F3A;
    border-radius: 10px;
    padding: 15px;
}
[data-testid="stMetricLabel"] {
    font-size: 14px;
    color: #9AA5B1;
}
[data-testid="stMetricValue"] {
    font-size: 26px;
}
h1 {
    padding-bottom: 10px;
    border-bottom: 2px solid #1E88E5;
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
}
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}
</style>
"""

PLOTLY_TEMPLATE = "plotly_dark"

PLOTLY_COLORS = {
    "primary": "#1E88E5",
    "good": "#2ECC71",
    "warning": "#F1C40F",
    "bad": "#E74C3C"
}


def apply_custom_style():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)