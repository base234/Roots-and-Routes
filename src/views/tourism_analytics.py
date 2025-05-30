import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils.database import execute_query
from datetime import datetime

def render_overview_tab(df):
    """Render the overview tab with key metrics and general analysis."""
    # Top row: Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Sites",
            len(df),
            help="Total number of heritage sites"
        )

    with col2:
        st.metric(
            "Total Visitors",
            f"{df['total_visitors'].sum():,.0f}",
            help="Total number of visitors across all sites"
        )

    with col3:
        st.metric(
            "Total Revenue",
            f"₹{df['total_revenue'].sum():,.0f}",
            help="Total revenue generated across all sites"
        )

    with col4:
        st.metric(
            "Avg Daily Visitors",
            f"{df['avg_daily_visitors'].mean():,.0f}",
            help="Average daily visitors per site"
        )

    st.markdown("---")

    # State-wise analysis
    st.subheader("State-wise Tourism Analysis")
    state_stats = df.groupby('state').agg({
        'total_visitors': 'sum',
        'total_revenue': 'sum',
        'site_name': 'count'
    }).reset_index()

    state_stats.columns = ['state', 'total_visitors', 'total_revenue', 'site_count']

    fig_state = px.bar(
        state_stats,
        x='state',
        y='total_visitors',
        title='Total Visitors by State',
        labels={'state': 'State', 'total_visitors': 'Total Visitors'},
        color='total_visitors',
        color_continuous_scale='Viridis'
    )

    st.plotly_chart(fig_state, use_container_width=True)

    # Heritage Type Analysis
    st.subheader("Heritage Type Analysis")
    type_stats = df.groupby('heritage_type').agg({
        'total_visitors': 'sum',
        'total_revenue': 'sum',
        'site_name': 'count'
    }).reset_index()

    type_stats.columns = ['heritage_type', 'total_visitors', 'total_revenue', 'site_count']

    fig_type = px.pie(
        type_stats,
        values='total_visitors',
        names='heritage_type',
        title='Visitor Distribution by Heritage Type',
        hole=0.4
    )

    st.plotly_chart(fig_type, use_container_width=True)

    # Top Performing Sites Table
    st.subheader("Top Performing Heritage Sites")

    # Sort and display top 10 sites
    top_sites = df.sort_values('total_visitors', ascending=False).head(10)

    # Format the data for display
    display_df = top_sites[[
        'site_name', 'state', 'heritage_type', 'total_visitors',
        'total_revenue', 'avg_daily_visitors'
    ]].copy()

    display_df.columns = [
        'Site Name', 'State', 'Heritage Type', 'Total Visitors',
        'Total Revenue (₹)', 'Avg Daily Visitors'
    ]

    # Format numbers
    display_df['Total Visitors'] = display_df['Total Visitors'].map('{:,.0f}'.format)
    display_df['Total Revenue (₹)'] = display_df['Total Revenue (₹)'].map('₹{:,.0f}'.format)
    display_df['Avg Daily Visitors'] = display_df['Avg Daily Visitors'].fillna(0).map('{:,.0f}'.format)

    st.dataframe(display_df, use_container_width=True)

def render_seasonal_analysis_tab(df):
    """Render the seasonal analysis tab."""

    # Get monthly visitor data
    query = """
    SELECT
        DATE_TRUNC('month', visit_date) as month,
        SUM(visitor_count) as monthly_visitors,
        SUM(revenue) as monthly_revenue
    FROM VISITOR_STATS
    GROUP BY DATE_TRUNC('month', visit_date)
    ORDER BY month
    """

    monthly_data = execute_query(query)

    if monthly_data:
        monthly_df = pd.DataFrame(monthly_data, columns=['month', 'monthly_visitors', 'monthly_revenue'])
        monthly_df['month'] = pd.to_datetime(monthly_df['month'])

        # Create line chart for monthly trends
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['monthly_visitors'],
            name='Visitors',
            line=dict(color='#1f77b4')
        ))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['monthly_revenue'],
            name='Revenue',
            line=dict(color='#2ca02c'),
            yaxis='y2'
        ))

        fig_monthly.update_layout(
            title='Monthly Visitor and Revenue Trends',
            xaxis_title='Month',
            yaxis_title='Visitors',
            yaxis2=dict(
                title='Revenue (₹)',
                overlaying='y',
                side='right'
            )
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

        # Peak season analysis
        peak_months = monthly_df.nlargest(4, 'monthly_visitors')

        col1, col2, col3, col4 = st.columns(4)
        for i, (_, row) in enumerate(peak_months.iterrows()):
            with [col1, col2, col3, col4][i]:
                st.metric(
                    f"Peak Month {i+1}",
                    row['month'].strftime('%B %Y'),
                    f"{row['monthly_visitors']:,.0f} visitors"
                )

def render_economic_impact_tab(df):
    """Render the economic impact analysis tab."""

    # Revenue distribution by state
    state_revenue = df.groupby('state')['total_revenue'].sum().reset_index()
    state_revenue = state_revenue.sort_values('total_revenue', ascending=False)

    fig_revenue = px.bar(
        state_revenue,
        x='state',
        y='total_revenue',
        title='Revenue Distribution by State',
        labels={'state': 'State', 'total_revenue': 'Total Revenue (₹)'},
        color='total_revenue',
        color_continuous_scale='Viridis'
    )

    st.plotly_chart(fig_revenue, use_container_width=True)

    # Revenue per visitor analysis
    st.subheader("Revenue per Visitor Analysis")

    # Handle null values in the data
    df_clean = df.copy()
    df_clean['total_revenue'] = df_clean['total_revenue'].fillna(0)
    df_clean['total_visitors'] = df_clean['total_visitors'].fillna(0)
    df_clean['revenue_per_visitor'] = df_clean['total_revenue'] / df_clean['total_visitors'].replace(0, 1)  # Avoid division by zero

    fig_rpv = px.scatter(
        df_clean,
        x='total_visitors',
        y='revenue_per_visitor',
        color='heritage_type',
        size='total_revenue',
        title='Revenue per Visitor vs Total Visitors',
        labels={
            'total_visitors': 'Total Visitors',
            'revenue_per_visitor': 'Revenue per Visitor (₹)',
            'heritage_type': 'Heritage Type'
        }
    )

    st.plotly_chart(fig_rpv, use_container_width=True)

def render_art_forms_tab():
    """Render the art forms analysis tab."""

    # Get art forms data
    query = """
    SELECT
        a.name as art_form,
        a.category,
        a.origin_state,
        a.practitioners_count,
        COUNT(DISTINCT saf.site_id) as associated_sites,
        SUM(v.visitor_count) as total_visitors
    FROM ART_FORMS a
    LEFT JOIN SITE_ART_FORMS saf ON a.art_form_id = saf.art_form_id
    LEFT JOIN VISITOR_STATS v ON saf.site_id = v.site_id
    GROUP BY a.name, a.category, a.origin_state, a.practitioners_count
    """

    art_forms_data = execute_query(query)

    if art_forms_data:
        art_df = pd.DataFrame(art_forms_data, columns=[
            'art_form', 'category', 'origin_state', 'practitioners_count',
            'associated_sites', 'total_visitors'
        ])

        # Art forms by category
        category_stats = art_df.groupby('category').agg({
            'art_form': 'count',
            'practitioners_count': 'sum',
            'total_visitors': 'sum'
        }).reset_index()

        fig_category = px.pie(
            category_stats,
            values='art_form',
            names='category',
            title='Distribution of Art Forms by Category',
            hole=0.4
        )

        st.plotly_chart(fig_category, use_container_width=True)

        # Top art forms by visitors
        top_art_forms = art_df.nlargest(10, 'total_visitors')

        fig_top_arts = px.bar(
            top_art_forms,
            x='art_form',
            y='total_visitors',
            color='category',
            title='Top 10 Art Forms by Visitor Interest',
            labels={
                'art_form': 'Art Form',
                'total_visitors': 'Total Visitors',
                'category': 'Category'
            }
        )

        st.plotly_chart(fig_top_arts, use_container_width=True)

def render_predictive_analysis_tab(df):
    """Render the predictive analysis tab."""

    # Calculate month-over-month growth
    query = """
    SELECT
        DATE_TRUNC('month', visit_date) as month,
        SUM(visitor_count) as monthly_visitors
    FROM VISITOR_STATS
    GROUP BY DATE_TRUNC('month', visit_date)
    ORDER BY month
    """

    monthly_data = execute_query(query)

    if monthly_data:
        monthly_df = pd.DataFrame(monthly_data, columns=['month', 'monthly_visitors'])
        monthly_df['month'] = pd.to_datetime(monthly_df['month'])
        monthly_df['growth_rate'] = monthly_df['monthly_visitors'].pct_change() * 100

        # Plot growth rate
        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['growth_rate'],
            name='Growth Rate',
            line=dict(color='#ff7f0e')
        ))

        fig_growth.update_layout(
            title='Month-over-Month Visitor Growth Rate',
            xaxis_title='Month',
            yaxis_title='Growth Rate (%)',
            showlegend=True
        )

        st.plotly_chart(fig_growth, use_container_width=True)

        # Display key metrics
        col1, col2 = st.columns(2)

        with col1:
            avg_growth = monthly_df['growth_rate'].mean()
            st.metric(
                "Average Monthly Growth",
                f"{avg_growth:.1f}%",
                help="Average month-over-month growth rate"
            )

        with col2:
            last_growth = monthly_df['growth_rate'].iloc[-1]
            st.metric(
                "Latest Growth Rate",
                f"{last_growth:.1f}%",
                help="Most recent month-over-month growth rate"
            )

def render_tourism_analytics():
    """Render the tourism analytics dashboard."""

    # Get visitor statistics
    query = """
    SELECT
        h.name as site_name,
        h.state,
        h.heritage_type,
        h.unesco_status,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        SUM(v.revenue) as total_revenue,
        AVG(v.visitor_count) as avg_daily_visitors,
        AVG(v.revenue) as avg_daily_revenue
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    GROUP BY h.name, h.state, h.heritage_type, h.unesco_status
    ORDER BY total_visitors DESC
    """

    results = execute_query(query)

    if results:
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            'site_name', 'state', 'heritage_type', 'unesco_status',
            'visit_days', 'total_visitors', 'total_revenue',
            'avg_daily_visitors', 'avg_daily_revenue'
        ])

        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Seasonal Analysis", "Economic Impact",
            "Art Forms", "Predictive Analysis"
        ])

        with tab1:
            render_overview_tab(df)

        with tab2:
            render_seasonal_analysis_tab(df)

        with tab3:
            render_economic_impact_tab(df)

        with tab4:
            render_art_forms_tab()

        with tab5:
            render_predictive_analysis_tab(df)

    else:
        st.error("No tourism data available.")
