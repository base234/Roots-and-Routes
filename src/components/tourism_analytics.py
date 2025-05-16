import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from utils.config import ANALYTICS_CONFIG
from utils.database import execute_query

def get_visitor_stats(start_date=None, end_date=None, site_id=None):
    """Fetch visitor statistics with optional filters."""
    query = """
    SELECT
        v.visit_date,
        h.name as site_name,
        h.state,
        h.heritage_type,
        v.visitor_count,
        v.revenue,
        EXTRACT(YEAR FROM v.visit_date) as year,
        EXTRACT(MONTH FROM v.visit_date) as month,
        EXTRACT(DAY FROM v.visit_date) as day,
        EXTRACT(DOW FROM v.visit_date) as day_of_week
    FROM VISITOR_STATS v
    JOIN HERITAGE_SITES h ON v.site_id = h.site_id
    WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND v.visit_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND v.visit_date <= %s"
        params.append(end_date)
    if site_id:
        query += " AND v.site_id = %s"
        params.append(site_id)

    query += " ORDER BY v.visit_date"
    return execute_query(query, params)

def get_site_clusters():
    """Perform clustering analysis on heritage sites."""
    query = """
    SELECT
        h.site_id,
        h.name,
        h.state,
        h.heritage_type,
        h.risk_level,
        h.health_index,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(v.revenue) as avg_revenue,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    GROUP BY h.site_id, h.name, h.state, h.heritage_type, h.risk_level, h.health_index
    """
    sites_df = execute_query(query)

    # Prepare features for clustering
    features = ['health_index', 'total_visitors', 'avg_revenue', 'avg_rating']
    X = sites_df[features].fillna(0)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Perform clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    sites_df['cluster'] = kmeans.fit_predict(X_scaled)

    return sites_df

def predict_visitors(df, periods=30):
    """Predict future visitor counts using Prophet."""
    # Prepare data for Prophet
    prophet_df = df.rename(columns={'visit_date': 'ds', 'visitor_count': 'y'})

    # Create and fit model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True
    )
    model.fit(prophet_df)

    # Make predictions
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast

def render_tourism_analytics():
    """Render the tourism analytics page."""
    st.title("Tourism Analytics")
    st.markdown("Analyze visitor patterns and predict future trends")

    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs([
        "Visitor Trends",
        "Predictive Analytics",
        "Site Clustering"
    ])

    with tab1:
        st.subheader("Visitor Trends Analysis")

        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                pd.Timestamp.now() - pd.Timedelta(days=365)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                pd.Timestamp.now()
            )

        # Fetch visitor statistics
        visitor_stats = get_visitor_stats(start_date, end_date)

        if not visitor_stats.empty:
            # Time series analysis
            st.subheader("Visitor Trends Over Time")

            # Aggregate data by date
            daily_stats = visitor_stats.groupby('visit_date').agg({
                'visitor_count': 'sum',
                'revenue': 'sum'
            }).reset_index()

            # Create time series plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_stats['visit_date'],
                y=daily_stats['visitor_count'],
                name='Daily Visitors',
                line=dict(color='#1E88E5')
            ))
            fig.add_trace(go.Scatter(
                x=daily_stats['visit_date'],
                y=daily_stats['revenue'],
                name='Daily Revenue',
                line=dict(color='#43A047'),
                yaxis='y2'
            ))
            fig.update_layout(
                title='Visitor and Revenue Trends',
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

            # State-wise analysis
            st.subheader("State-wise Visitor Distribution")
            state_stats = visitor_stats.groupby('state').agg({
                'visitor_count': 'sum',
                'revenue': 'sum'
            }).reset_index()

            fig = px.bar(
                state_stats,
                x='state',
                y='visitor_count',
                title='Total Visitors by State',
                color='revenue',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Heritage type analysis
            st.subheader("Heritage Type Analysis")
            type_stats = visitor_stats.groupby('heritage_type').agg({
                'visitor_count': 'sum',
                'revenue': 'mean'
            }).reset_index()

            fig = px.pie(
                type_stats,
                values='visitor_count',
                names='heritage_type',
                title='Visitor Distribution by Heritage Type'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Predictive Analytics")

        # Site selection for prediction
        site_query = "SELECT DISTINCT name FROM HERITAGE_SITES ORDER BY name"
        sites = execute_query(site_query)
        selected_site = st.selectbox("Select Site for Prediction", sites['name'])

        if selected_site:
            # Get historical data for selected site
            site_id_query = "SELECT site_id FROM HERITAGE_SITES WHERE name = %s"
            site_id = execute_query(site_id_query, [selected_site]).iloc[0]['site_id']

            visitor_stats = get_visitor_stats(
                start_date=pd.Timestamp.now() - pd.Timedelta(days=365),
                site_id=site_id
            )

            if not visitor_stats.empty:
                # Make predictions
                forecast = predict_visitors(
                    visitor_stats,
                    periods=ANALYTICS_CONFIG['prediction_horizon']
                )

                # Plot predictions
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=visitor_stats['visit_date'],
                    y=visitor_stats['visitor_count'],
                    name='Historical Data',
                    line=dict(color='#1E88E5')
                ))
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=forecast['yhat'],
                    name='Prediction',
                    line=dict(color='#43A047')
                ))
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=forecast['yhat_upper'],
                    name='Upper Bound',
                    line=dict(color='rgba(67, 160, 71, 0.2)'),
                    fill=None
                ))
                fig.add_trace(go.Scatter(
                    x=forecast['ds'],
                    y=forecast['yhat_lower'],
                    name='Lower Bound',
                    line=dict(color='rgba(67, 160, 71, 0.2)'),
                    fill='tonexty'
                ))
                fig.update_layout(
                    title=f'Visitor Prediction for {selected_site}',
                    xaxis_title='Date',
                    yaxis_title='Daily Visitors',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display prediction metrics
                st.subheader("Prediction Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Predicted Daily Visitors",
                        f"{forecast['yhat'].mean():.0f}"
                    )
                with col2:
                    st.metric(
                        "Prediction Confidence",
                        f"{ANALYTICS_CONFIG['confidence_interval']*100}%"
                    )
                with col3:
                    st.metric(
                        "Prediction Horizon",
                        f"{ANALYTICS_CONFIG['prediction_horizon']} days"
                    )

    with tab3:
        st.subheader("Site Clustering Analysis")

        # Perform clustering
        sites_df = get_site_clusters()

        if not sites_df.empty:
            # Display cluster characteristics
            st.write("Cluster Characteristics")
            cluster_stats = sites_df.groupby('cluster').agg({
                'health_index': 'mean',
                'total_visitors': 'mean',
                'avg_revenue': 'mean',
                'avg_rating': 'mean'
            }).round(2)
            st.dataframe(cluster_stats)

            # Visualize clusters
            fig = px.scatter(
                sites_df,
                x='health_index',
                y='total_visitors',
                color='cluster',
                size='avg_revenue',
                hover_data=['name', 'state', 'heritage_type'],
                title='Heritage Sites Clustering'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display sites in each cluster
            st.subheader("Sites by Cluster")
            for cluster in sorted(sites_df['cluster'].unique()):
                with st.expander(f"Cluster {cluster}"):
                    cluster_sites = sites_df[sites_df['cluster'] == cluster]
                    st.dataframe(
                        cluster_sites[[
                            'name',
                            'state',
                            'heritage_type',
                            'health_index',
                            'total_visitors',
                            'avg_revenue',
                            'avg_rating'
                        ]]
                    )
