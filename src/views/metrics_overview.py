import streamlit as st
import pandas as pd
from src.utils.dashboard_utils import DashboardUtils
from src.components.header import render_header
from src.components.footer import render_footer

def render_metrics_overview():
    # Initialize dashboard utilities
    dashboard = DashboardUtils()

    # Overview Metrics
    metrics = dashboard.get_overview_metrics()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sites", metrics['total_sites'])
    with col2:
        st.metric("Total Visitors", f"{metrics['total_visitors']:,}")
    with col3:
        st.metric("Total Revenue", f"₹{metrics['total_revenue']:,}")
    with col4:
        st.metric("Average Health", f"{metrics['avg_health']:.1f}")

    # Visitor Trends
    st.subheader("Visitor Trends")
    visitor_trends = dashboard.get_visitor_trends()
    visitor_chart = dashboard.create_visitor_trend_chart(visitor_trends)
    if visitor_chart is not None:
        st.plotly_chart(visitor_chart, use_container_width=True)
    else:
        st.info("No visitor trend data available at the moment.")

    # Heritage Type Distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Heritage Type Distribution")
        type_dist = dashboard.get_heritage_type_distribution()
        if type_dist:
            type_chart = dashboard.create_heritage_type_chart(type_dist)
            if type_chart is not None:
                st.plotly_chart(type_chart, use_container_width=True)
            else:
                st.info("No heritage type distribution data available.")
        else:
            st.info("No heritage type distribution data available.")

    # State-wise Distribution
    with col2:
        st.subheader("State-wise Distribution")
        state_dist = dashboard.get_state_wise_distribution()
        if state_dist:
            state_chart = dashboard.create_state_distribution_chart(state_dist)
            if state_chart is not None:
                st.plotly_chart(state_chart, use_container_width=True)
            else:
                st.info("No state-wise distribution data available.")
        else:
            st.info("No state-wise distribution data available.")

    # Trending Sites
    st.subheader("Trending Heritage Sites")
    trending_sites = dashboard.get_trending_sites()
    if trending_sites:
        for site in trending_sites:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {site['name']}")
                    st.markdown(f"**{site['location']}, {site['state']}**")
                with col2:
                    st.metric("Visitors", f"{site['total_visitors']:,}")
                    st.metric("Rating", f"{site['avg_rating']:.1f} ⭐")
                st.divider()
    else:
        st.info("No trending sites data available at the moment.")

    # Health Index
    st.subheader("Heritage Health Index")
    health_index = dashboard.get_health_index_summary()
    if health_index:
        health_chart = dashboard.create_health_index_chart(health_index)
        if health_chart is not None:
            st.plotly_chart(health_chart, use_container_width=True)
        else:
            st.info("No health index chart data available.")
    else:
        st.info("No health index data available at the moment.")

if __name__ == "__main__":
    render_metrics_overview()
