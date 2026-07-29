import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from database.models import get_engine
from intelligence.health_score import calculate_health_score
from monitoring.conversion_metrics import overall_conversion_rate, conversion_by_channel
import streamlit as st
from database.models import get_engine
from intelligence.health_score import calculate_health_score
from monitoring.conversion_metrics import overall_conversion_rate, conversion_by_channel

st.set_page_config(
    page_title="SkyFunnel Intelligence",
    page_icon="✈️",
    layout="wide"
)

engine = get_engine()

st.title("✈️ SkyFunnel Intelligence")
st.caption("Flight Booking Conversion Intelligence Platform")

health = calculate_health_score(engine)

status_colors = {
    "HEALTHY": "🟢",
    "MONITOR": "🟡",
    "WARNING": "🟠",
    "CRITICAL": "🔴"
}

st.header(f"{status_colors.get(health['status'], '')} Booking Health Score")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Overall Score", f"{health['overall_score']} / 100", health["status"])
col2.metric("Conversion Health", f"{health['conversion_score']} / 100")
col3.metric("Anomaly Health", f"{health['anomaly_score']} / 100", health["significant_anomalies"])
col4.metric("Impact Health", f"{health['impact_score']} / 100", f"-{health['estimated_lost_bookings']} bookings")
col5.metric("Channel Health", f"{health['channel_score']} / 100", f"{health['channel_gap']:.1%} gap")

st.divider()

st.subheader("Overall Conversion")
overall = overall_conversion_rate(engine)
st.metric("Platform-wide Conversion Rate", f"{overall:.2%}")

st.subheader("Conversion by Channel")
channel_df = conversion_by_channel(engine)
st.dataframe(channel_df, use_container_width=True)

st.divider()
st.caption("Use the sidebar to navigate to Route Intelligence, Incident History, and more.")