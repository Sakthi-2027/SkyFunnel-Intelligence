import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from database.models import get_engine
from intelligence.root_cause import explain_channel_gap, explain_route
from intelligence.health_score import get_monitored_routes
from intelligence.business_impact import calculate_route_impact
from reports.executive_report import build_report

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
from dashboard.styles import apply_custom_style
apply_custom_style()

engine = get_engine()

st.title("🤖 AI Insights")

st.subheader("Channel Performance Analysis")
st.text(explain_channel_gap(engine))

st.divider()

st.subheader("Route Root Cause Explorer")
monitored_routes = get_monitored_routes(engine)
selected_route = st.selectbox("Select a route to investigate", sorted(monitored_routes))

if selected_route:
    st.text(explain_route(engine, selected_route))

st.divider()

st.subheader("Full Executive Report")
if st.button("Generate Latest Report"):
    with st.spinner("Analyzing all routes and generating report..."):
        report_text = build_report(engine)
    st.text(report_text)
    st.download_button(
        "Download Report as TXT",
        report_text,
        file_name="skyfunnel_executive_report.txt",
        mime="text/plain"
    )