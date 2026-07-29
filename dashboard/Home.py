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

status_styles = {
    "HEALTHY": ("🟢", "#2ECC71"),
    "MONITOR": ("🟡", "#F1C40F"),
    "WARNING": ("🟠", "#E67E22"),
    "CRITICAL": ("🔴", "#E74C3C")
}
emoji, color = status_styles.get(health["status"], ("", "#FFFFFF"))

st.markdown(
    f"""
    <div style="padding: 20px; border-radius: 10px; background-color: {color}22;
                border: 1px solid {color}; margin-bottom: 20px;">
        <span style="font-size: 28px;">{emoji} {health['status']}</span>
        <span style="font-size: 20px; float: right;">
            Score: <b>{health['overall_score']} / 100</b>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Conversion Health", f"{health['conversion_score']} / 100")
col2.metric("Anomaly Health", f"{health['anomaly_score']} / 100", health["significant_anomalies"])
col3.metric("Impact Health", f"{health['impact_score']} / 100", f"-{health['estimated_lost_bookings']} bookings")
col4.metric("Channel Health", f"{health['channel_score']} / 100", f"{health['channel_gap']:.1%} gap")
st.divider()

st.subheader("Overall Conversion")
overall = overall_conversion_rate(engine)
st.metric("Platform-wide Conversion Rate", f"{overall:.2%}")

st.subheader("Conversion by Channel")
channel_df = conversion_by_channel(engine)
st.dataframe(channel_df, use_container_width=True)

st.divider()
st.caption("Use the sidebar to navigate to Route Intelligence, Incident History, and more.")