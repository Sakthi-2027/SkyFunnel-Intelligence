import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import plotly.express as px
from database.models import get_engine
from monitoring.conversion_metrics import conversion_by_route

st.set_page_config(page_title="Route Intelligence", page_icon="🛫", layout="wide")
from dashboard.styles import apply_custom_style
apply_custom_style()

engine = get_engine()

st.title("🛫 Route Intelligence")

min_bookings = st.slider("Minimum bookings per route", min_value=10, max_value=500, value=50, step=10)

routes_df = conversion_by_route(engine, min_bookings=min_bookings)

search = st.text_input("Search route code (e.g. DEL, ICN)")
if search:
    routes_df = routes_df[routes_df["route"].str.contains(search.upper())]

st.subheader(f"Showing {len(routes_df)} routes with at least {min_bookings} bookings")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Top 15 Routes by Conversion**")
    top_15 = routes_df.head(15)
    fig_top = px.bar(top_15, x="route", y="conversion_rate", color="conversion_rate",
                     color_continuous_scale="Greens", template="plotly_dark")
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.markdown("**Bottom 15 Routes by Conversion**")
    bottom_15 = routes_df.tail(15)
    fig_bottom = px.bar(bottom_15, x="route", y="conversion_rate", color="conversion_rate",
                        color_continuous_scale="Reds_r", template="plotly_dark")
    st.plotly_chart(fig_bottom, use_container_width=True)

st.divider()
st.subheader("Full Route Table")
st.dataframe(
    routes_df.style.format({"conversion_rate": "{:.2%}"}),
    use_container_width=True,
    height=400
)