import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.utils.database_config import snowflake_config

class DashboardUtils:
    def __init__(self):
        self.sf = snowflake_config

    def get_overview_metrics(self):
        """Get overview metrics for the dashboard."""
        query = """
        SELECT
            COUNT(DISTINCT h.site_id) as total_sites,
            SUM(v.visitor_count) as total_visitors,
            SUM(v.revenue) as total_revenue,
            AVG(h.health_index) as avg_health
        FROM HERITAGE_SITES h
        LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
        """
        result = self.sf.execute_query(query)

        # Return default values if query fails or returns no results
        if result is None or len(result) == 0:
            return {
                'total_sites': 0,
                'total_visitors': 0,
                'total_revenue': 0,
                'avg_health': 0
            }

        # Convert the result to a dictionary
        metrics = {
            'total_sites': result[0][0] or 0,
            'total_visitors': result[0][1] or 0,
            'total_revenue': result[0][2] or 0,
            'avg_health': result[0][3] or 0
        }
        return metrics

    def get_trending_sites(self, limit=5):
        """Get trending heritage sites based on visitor count and ratings."""
        query = """
        SELECT
            h.name,
            h.location,
            h.state,
            COUNT(DISTINCT v.visit_date) as visit_days,
            SUM(v.visitor_count) as total_visitors,
            AVG(u.rating) as avg_rating
        FROM HERITAGE_SITES h
        LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
        LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
        GROUP BY h.name, h.location, h.state
        ORDER BY total_visitors DESC, avg_rating DESC
        LIMIT %s
        """
        result = self.sf.execute_query(query, [limit])

        # Return empty list if query fails or returns no results
        if result is None:
            return []

        # Convert the result to a list of dictionaries
        sites = []
        for row in result:
            site = {
                'name': row[0],
                'location': row[1],
                'state': row[2],
                'visit_days': row[3] or 0,
                'total_visitors': row[4] or 0,
                'avg_rating': row[5] or 0
            }
            sites.append(site)

        return sites

    def get_visitor_trends(self, months=12):
        """Get visitor trends over time."""
        query = """
        SELECT
            DATE_TRUNC('month', visit_date) as month,
            COALESCE(SUM(visitor_count), 0) as total_visitors,
            COALESCE(SUM(revenue), 0) as total_revenue
        FROM VISITOR_STATS
        WHERE visit_date >= DATEADD(month, -%s, CURRENT_DATE())
        GROUP BY month
        ORDER BY month ASC
        """
        result = self.sf.execute_query(query, [months])

        # Return default values if query fails or returns no results
        if result is None or len(result) == 0:
            return []

        return result

    def get_heritage_type_distribution(self):
        """Get distribution of heritage sites by type."""
        query = """
        SELECT
            heritage_type,
            COUNT(*) as count
        FROM HERITAGE_SITES
        GROUP BY heritage_type
        """
        return self.sf.execute_query(query)

    def get_state_wise_distribution(self):
        """Get distribution of heritage sites by state."""
        query = """
        SELECT
            h.state,
            COUNT(*) as count,
            SUM(v.visitor_count) as total_visitors
        FROM HERITAGE_SITES h
        LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
        GROUP BY h.state
        """
        return self.sf.execute_query(query)

    def get_health_index_summary(self):
        """Get summary of heritage health index."""
        query = """
        SELECT
            AVG(h.health_index) as avg_health,
            COUNT(DISTINCT CASE WHEN h.risk_level = 'Low' THEN h.site_id END) as low_risk_count,
            COUNT(DISTINCT CASE WHEN h.risk_level = 'Medium' THEN h.site_id END) as medium_risk_count,
            COUNT(DISTINCT CASE WHEN h.risk_level = 'High' THEN h.site_id END) as high_risk_count,
            COUNT(DISTINCT v.visit_date) as total_visit_days,
            SUM(v.visitor_count) as total_visitors,
            AVG(u.rating) as avg_rating
        FROM HERITAGE_SITES h
        LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
        LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
        """
        result = self.sf.execute_query(query)

        # Return default values if query fails or returns no results
        if result is None or len(result) == 0:
            return {
                'avg_health': 0,
                'low_risk_count': 0,
                'medium_risk_count': 0,
                'high_risk_count': 0,
                'total_visit_days': 0,
                'total_visitors': 0,
                'avg_rating': 0
            }

        # Convert the result to a dictionary
        health_index = {
            'avg_health': result[0][0] or 0,
            'low_risk_count': result[0][1] or 0,
            'medium_risk_count': result[0][2] or 0,
            'high_risk_count': result[0][3] or 0,
            'total_visit_days': result[0][4] or 0,
            'total_visitors': result[0][5] or 0,
            'avg_rating': result[0][6] or 0
        }
        return health_index

    def create_visitor_trend_chart(self, data):
        """Create a line chart for visitor trends."""
        if not data:
            st.warning("No visitor trend data available")
            return None

        df = pd.DataFrame(data, columns=['month', 'total_visitors', 'total_revenue'])

        # Convert month to datetime if it's not already
        df['month'] = pd.to_datetime(df['month'])

        fig = go.Figure()

        # Add visitor count line
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['total_visitors'],
            name='Visitors',
            line=dict(color='#1f77b4')
        ))

        # Add revenue line
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['total_revenue'],
            name='Revenue',
            line=dict(color='#2ca02c'),
            yaxis='y2'
        ))

        # Update layout
        fig.update_layout(
            title='Visitor and Revenue Trends',
            xaxis_title='Month',
            yaxis_title='Number of Visitors',
            yaxis2=dict(
                title='Revenue (₹)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            showlegend=True
        )

        return fig

    def create_heritage_type_chart(self, data):
        """Create a pie chart for heritage type distribution."""
        df = pd.DataFrame(data, columns=['heritage_type', 'count'])
        fig = px.pie(
            df,
            values='count',
            names='heritage_type',
            title='Distribution of Heritage Sites by Type'
        )
        return fig

    def create_state_distribution_chart(self, data):
        """Create a bar chart for state-wise distribution."""
        df = pd.DataFrame(data, columns=['state', 'count', 'total_visitors'])
        fig = px.bar(
            df,
            x='state',
            y='count',
            title='Distribution of Heritage Sites by State',
            color='total_visitors',
            color_continuous_scale='Viridis'
        )
        return fig

    def create_health_index_chart(self, data):
        """Create a radar chart for health index metrics."""
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[
                data['avg_health'],
                data['low_risk_count'],
                data['medium_risk_count'],
                data['high_risk_count'],
                data['total_visitors']
            ],
            theta=['Health Index', 'Low Risk', 'Medium Risk', 'High Risk', 'Total Visitors'],
            fill='toself',
            name='Health Metrics'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )

        return fig

    def test_connection(self):
        """Test the database connection."""
        query = "SELECT COUNT(*) FROM HERITAGE_SITES"
        result = self.sf.execute_query(query)
        return result is not None and len(result) > 0
