import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import get_engine

st.set_page_config(page_title="Incident History", page_icon="📅", layout="wide")

engine = get_engine()

st.title("📅 Incident History")

df = pd.read_sql("SELECT * FROM incidents ORDER BY estimated_lost_bookings DESC", con=engine)

col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(df))
col2.metric("High Severity", len(df[df["severity"] == "HIGH"]))
col3.metric("Total Estimated Lost Bookings", f"{df['estimated_lost_bookings'].sum():.1f}")

st.divider()

severity_filter = st.multiselect(
    "Filter by severity", options=df["severity"].unique().tolist(),
    default=df["severity"].unique().tolist()
)
status_filter = st.multiselect(
    "Filter by status", options=df["status"].unique().tolist(),
    default=df["status"].unique().tolist()
)

filtered_df = df[df["severity"].isin(severity_filter) & df["status"].isin(status_filter)]

st.subheader(f"Showing {len(filtered_df)} of {len(df)} incidents")

fig = px.bar(
    filtered_df.head(20), x="route", y="estimated_lost_bookings",
    color="severity", color_discrete_map={"HIGH": "#E74C3C", "MEDIUM": "#F1C40F", "LOW": "#2ECC71"}
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    filtered_df[["route", "origin", "observed_rate", "baseline_rate",
                 "p_value", "estimated_lost_bookings", "severity", "status", "detected_at"]]
    .style.format({"observed_rate": "{:.2%}", "baseline_rate": "{:.2%}", "p_value": "{:.4f}"}),
    use_container_width=True,
    height=500
)

st.download_button(
    "Download filtered incidents as CSV",
    filtered_df.to_csv(index=False),
    file_name="skyfunnel_incidents.csv",
    mime="text/csv"
)