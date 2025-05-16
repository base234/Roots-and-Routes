import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import googlemaps
from utils.config import (
    DASHBOARD_CONFIG,
    GOOGLE_MAPS_API_KEY,
    SNOWFLAKE_CONFIG
)
from utils.database import get_db_connection

def get_overview_metrics():
    """Fetch overview metrics from the database."""
    conn = get_db_connection()
    try:
        # Total heritage sites
        sites_query = "SELECT COUNT(*) as total_sites FROM HERITAGE_SITES"
        total_sites = pd.read_sql(sites_query, conn).iloc[0]['total_sites']

        # Total visitors (last 30 days)
        visitors_query = """
        SELECT SUM(visitor_count) as total_visitors
        FROM VISITOR_STATS
        WHERE visit_date >= DATEADD(day, -30, CURRENT_DATE())
        """
        total_visitors = pd.read_sql(visitors_query, conn).iloc[0]['total_visitors']

        # Total revenue (last 30 days)
        revenue_query = """
        SELECT SUM(revenue) as total_revenue
        FROM VISITOR_STATS
        WHERE visit_date >= DATEADD(day, -30, CURRENT_DATE())
        """
        total_revenue = pd.read_sql(revenue_query, conn).iloc[0]['total_revenue']

        # Average health index
        health_query = "SELECT AVG(health_index) as avg_health FROM HERITAGE_SITES"
        avg_health = pd.read_sql(health_query, conn).iloc[0]['avg_health']

        return {
            'total_sites': total_sites,
            'total_visitors': total_visitors,
            'total_revenue': total_revenue,
            'avg_health': avg_health
        }
    finally:
        conn.close()

def get_trending_sites():
    """Fetch trending heritage sites based on visitor count and ratings."""
    conn = get_db_connection()
    try:
        query = """
        WITH site_metrics AS (
            SELECT
                h.site_id,
                h.name,
                h.state,
                h.heritage_type,
                COUNT(DISTINCT v.visit_date) as visit_days,
                SUM(v.visitor_count) as total_visitors,
                AVG(u.rating) as avg_rating
            FROM HERITAGE_SITES h
            LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
            LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
            WHERE v.visit_date >= DATEADD(day, -30, CURRENT_DATE())
            GROUP BY h.site_id, h.name, h.state, h.heritage_type
        )
        SELECT *
        FROM site_metrics
        ORDER BY total_visitors DESC, avg_rating DESC
        LIMIT 5
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_visitor_trends():
    """Fetch visitor trends for time series analysis."""
    conn = get_db_connection()
    try:
        query = """
        SELECT
            visit_date,
            SUM(visitor_count) as daily_visitors,
            SUM(revenue) as daily_revenue
        FROM VISITOR_STATS
        WHERE visit_date >= DATEADD(day, -90, CURRENT_DATE())
        GROUP BY visit_date
        ORDER BY visit_date
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def create_heritage_map():
    """Create an interactive map of heritage sites."""
    conn = get_db_connection()
    try:
        query = """
        SELECT
            name,
            latitude,
            longitude,
            heritage_type,
            risk_level,
            health_index
        FROM HERITAGE_SITES
        """
        sites_df = pd.read_sql(query, conn)

        # Create base map centered on India
        m = folium.Map(
            location=DASHBOARD_CONFIG['default_map_center'],
            zoom_start=DASHBOARD_CONFIG['default_map_zoom']
        )

        # Add markers for each site
        for _, site in sites_df.iterrows():
            # Customize marker color based on risk level
            color = {
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red',
                'Critical': 'darkred'
            }.get(site['risk_level'], 'blue')

            # Create popup content
            popup_content = f"""
            <b>{site['name']}</b><br>
            Type: {site['heritage_type']}<br>
            Risk Level: {site['risk_level']}<br>
            Health Index: {site['health_index']:.2f}
            """

            # Add marker
            folium.Marker(
                location=[site['latitude'], site['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)

        return m
    finally:
        conn.close()

def render_dashboard():
    """Render the main dashboard."""
    st.title("Dashboard Overview")
    st.markdown("Welcome to Roots and Routes - Your Cultural Heritage Tourism Platform")

    # Overview Metrics
    metrics = get_overview_metrics()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Heritage Sites", metrics['total_sites'])
    with col2:
        st.metric("Monthly Visitors", f"{metrics['total_visitors']:,}")
    with col3:
        st.metric("Monthly Revenue", f"₹{metrics['total_revenue']:,.2f}")
    with col4:
        st.metric("Average Health Index", f"{metrics['avg_health']:.2f}")

    # Trending Sites
    st.subheader("Trending Heritage Sites")
    trending_sites = get_trending_sites()
    if not trending_sites.empty:
        fig = px.bar(
            trending_sites,
            x='name',
            y='total_visitors',
            color='avg_rating',
            title='Top 5 Trending Sites by Visitors',
            labels={'name': 'Site Name', 'total_visitors': 'Total Visitors', 'avg_rating': 'Average Rating'},
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Visitor Trends
    st.subheader("Visitor Trends")
    visitor_trends = get_visitor_trends()
    if not visitor_trends.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=visitor_trends['visit_date'],
            y=visitor_trends['daily_visitors'],
            name='Daily Visitors',
            line=dict(color='#1E88E5')
        ))
        fig.add_trace(go.Scatter(
            x=visitor_trends['visit_date'],
            y=visitor_trends['daily_revenue'],
            name='Daily Revenue',
            line=dict(color='#43A047'),
            yaxis='y2'
        ))
        fig.update_layout(
            title='90-Day Visitor and Revenue Trends',
            xaxis_title='Date',
            yaxis_title='Daily Visitors',
            yaxis2=dict(
                title='Daily Revenue (₹)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Interactive Map
    st.subheader("Heritage Sites Map")
    heritage_map = create_heritage_map()
    folium_static(heritage_map, width=800, height=600)

    # Quick Statistics
    st.subheader("Quick Statistics")
    col1, col2 = st.columns(2)

    with col1:
        # Heritage Types Distribution
        conn = get_db_connection()
        try:
            type_query = """
            SELECT heritage_type, COUNT(*) as count
            FROM HERITAGE_SITES
            GROUP BY heritage_type
            """
            type_df = pd.read_sql(type_query, conn)
            fig = px.pie(
                type_df,
                values='count',
                names='heritage_type',
                title='Distribution of Heritage Types'
            )
            st.plotly_chart(fig, use_container_width=True)
        finally:
            conn.close()

    with col2:
        # Risk Level Distribution
        conn = get_db_connection()
        try:
            risk_query = """
            SELECT risk_level, COUNT(*) as count
            FROM HERITAGE_SITES
            GROUP BY risk_level
            """
            risk_df = pd.read_sql(risk_query, conn)
            fig = px.bar(
                risk_df,
                x='risk_level',
                y='count',
                title='Distribution of Risk Levels',
                color='risk_level',
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red',
                    'Critical': 'darkred'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        finally:
            conn.close()
