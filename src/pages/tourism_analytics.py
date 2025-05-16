import streamlit as st
import pandas as pd
from utils.dashboard_utils import DashboardUtils
from components.header import render_header
from components.footer import render_footer

def render_overview_tab(dashboard):
    """Render the overview tab."""
    st.subheader("Tourism Overview")

    # Get overview metrics
    metrics = dashboard.get_overview_metrics()

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Visitors", f"{metrics['total_visitors']:,}")
    with col2:
        st.metric("Total Revenue", f"₹{metrics['total_revenue']:,}")
    with col3:
        st.metric("Average Health", f"{metrics['avg_health']:.1f}")

    # Visitor trends
    st.subheader("Visitor Trends")
    visitor_trends = dashboard.get_visitor_trends()
    visitor_chart = dashboard.create_visitor_trend_chart(visitor_trends)
    if visitor_chart is not None:
        st.plotly_chart(visitor_chart, use_container_width=True)
    else:
        st.info("No visitor trend data available at the moment.")

def render_seasonal_analysis_tab(dashboard):
    """Render the seasonal analysis tab."""
    st.subheader("Seasonal Analysis")

    # Get visitor trends by month
    visitor_trends = dashboard.get_visitor_trends(months=24)  # 2 years of data
    if not visitor_trends:
        st.info("No visitor trend data available at the moment.")
        return

    df = pd.DataFrame(visitor_trends, columns=['month', 'total_visitors', 'total_revenue'])
    if df.empty:
        st.info("No seasonal data available.")
        return

    df['month'] = pd.to_datetime(df['month'])
    df['month_name'] = df['month'].dt.strftime('%B')
    df['year'] = df['month'].dt.year

    # Create seasonal heatmap
    pivot_df = df.pivot_table(
        values='total_visitors',
        index='month_name',
        columns='year',
        aggfunc='mean'
    )

    if not pivot_df.empty:
        st.subheader("Monthly Visitor Distribution")
        st.dataframe(pivot_df.style.background_gradient())

        # Monthly averages
        st.subheader("Average Monthly Visitors")
        monthly_avg = df.groupby('month_name')['total_visitors'].mean().sort_values(ascending=False)
        st.bar_chart(monthly_avg)
    else:
        st.info("No monthly distribution data available.")

def render_economic_impact_tab(dashboard):
    """Render the economic impact tab."""
    st.subheader("Economic Impact Analysis")

    # Get visitor trends with revenue
    visitor_trends = dashboard.get_visitor_trends(months=12)
    if not visitor_trends:
        st.info("No visitor trend data available at the moment.")
        return

    df = pd.DataFrame(visitor_trends, columns=['month', 'total_visitors', 'total_revenue'])
    if df.empty:
        st.info("No economic data available.")
        return

    # Calculate metrics with zero checks
    total_revenue = df['total_revenue'].sum()
    total_visitors = df['total_visitors'].sum()
    avg_revenue_per_visitor = total_revenue / total_visitors if total_visitors > 0 else 0
    peak_revenue = df['total_revenue'].max()
    lowest_revenue = df['total_revenue'].min()

    # Revenue analysis
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue:,}")
        st.metric("Average Revenue per Visitor", f"₹{avg_revenue_per_visitor:.2f}")

    with col2:
        st.metric("Peak Month Revenue", f"₹{peak_revenue:,}")
        st.metric("Lowest Month Revenue", f"₹{lowest_revenue:,}")

    # Revenue trend
    st.subheader("Revenue Trend")
    st.line_chart(df.set_index('month')['total_revenue'])

def render_art_forms_tab(dashboard):
    """Render the art forms tab."""
    st.subheader("Art Forms Analysis")

    # Get heritage type distribution
    type_dist = dashboard.get_heritage_type_distribution()
    if not type_dist:
        st.info("No heritage type distribution data available.")
        return

    df = pd.DataFrame(type_dist, columns=['heritage_type', 'count'])

    # Display distribution
    st.subheader("Distribution of Heritage Types")
    type_chart = dashboard.create_heritage_type_chart(type_dist)
    if type_chart is not None:
        st.plotly_chart(type_chart, use_container_width=True)
    else:
        st.info("No heritage type chart data available.")

    # Get trending sites by type
    trending_sites = dashboard.get_trending_sites(limit=10)
    if trending_sites:
        df_sites = pd.DataFrame(trending_sites,
                              columns=['name', 'location', 'state', 'total_visitors', 'average_rating'])

        st.subheader("Top Heritage Sites by Type")
        st.dataframe(df_sites, use_container_width=True)
    else:
        st.info("No trending sites data available.")

def render_predictive_analytics_tab(dashboard):
    """Render the predictive analytics tab."""
    st.subheader("Predictive Analytics")

    # Get visitor trends
    visitor_trends = dashboard.get_visitor_trends(months=24)
    if not visitor_trends:
        st.info("No visitor trend data available at the moment.")
        return

    df = pd.DataFrame(visitor_trends, columns=['month', 'total_visitors', 'total_revenue'])
    if df.empty:
        st.info("No predictive analytics data available.")
        return

    # Simple moving average prediction
    df['visitor_ma'] = df['total_visitors'].rolling(window=3).mean()

    st.subheader("Visitor Forecast")
    st.line_chart(df.set_index('month')[['total_visitors', 'visitor_ma']], use_container_width=True)

    # Seasonal patterns
    st.subheader("Seasonal Patterns")
    df['month'] = pd.to_datetime(df['month'])
    monthly_avg = df.groupby(df['month'].dt.month)['total_visitors'].mean()
    st.bar_chart(monthly_avg, use_container_width=True)

def render_tourism_analytics():
    """Render the tourism analytics page."""
    render_header()

    st.title("Tourism Analytics")

    # Initialize dashboard utilities
    dashboard = DashboardUtils()

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Seasonal Analysis", "Economic Impact",
        "Art Forms", "Predictive Analytics"
    ])

    with tab1:
        render_overview_tab(dashboard)

    with tab2:
        render_seasonal_analysis_tab(dashboard)

    with tab3:
        render_economic_impact_tab(dashboard)

    with tab4:
        render_art_forms_tab(dashboard)

    with tab5:
        render_predictive_analytics_tab(dashboard)

    render_footer()

if __name__ == "__main__":
    render_tourism_analytics()
