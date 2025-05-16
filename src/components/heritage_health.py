import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import execute_query
from utils.config import HEALTH_CONFIG

def get_heritage_sites():
    """Fetch heritage sites with their health metrics."""
    query = """
    SELECT
        h.*,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    GROUP BY h.site_id, h.name, h.description, h.location, h.latitude, h.longitude,
             h.state, h.city, h.established_year, h.heritage_type, h.unesco_status,
             h.risk_level, h.health_index
    """
    return execute_query(query)

def get_art_forms(site_id):
    """Fetch art forms associated with a heritage site."""
    query = """
    SELECT a.*
    FROM ART_FORMS a
    JOIN SITE_ART_FORMS sa ON a.art_form_id = sa.art_form_id
    WHERE sa.site_id = %s
    """
    return execute_query(query, [site_id])

def get_health_trends(site_id):
    """Fetch health index trends for a site."""
    query = """
    SELECT
        visit_date,
        health_index,
        risk_level
    FROM HERITAGE_HEALTH_MONITORING
    WHERE site_id = %s
    ORDER BY visit_date
    """
    return execute_query(query, [site_id])

def calculate_preservation_score(site_data, art_forms):
    """Calculate a comprehensive preservation score for a site."""
    # Base score from health index
    base_score = site_data['health_index'] * 0.4

    # Risk level adjustment
    risk_multiplier = {
        'Low': 1.0,
        'Medium': 0.8,
        'High': 0.6,
        'Critical': 0.4
    }.get(site_data['risk_level'], 0.5)
    risk_score = base_score * risk_multiplier

    # Art forms preservation score
    art_forms_score = 0
    if not art_forms.empty:
        art_forms_risk = {
            'Low': 1.0,
            'Medium': 0.8,
            'High': 0.6,
            'Critical': 0.4
        }
        art_forms_score = sum(
            art_forms_risk.get(row['risk_level'], 0.5)
            for _, row in art_forms.iterrows()
        ) / len(art_forms)
    art_forms_score *= 0.3

    # Visitor impact score
    visitor_score = min(site_data['total_visitors'] / 10000, 1.0) * 0.3

    return (risk_score + art_forms_score + visitor_score) * 100

def generate_preservation_insights(site_data, art_forms, health_trends):
    """Generate preservation insights for a heritage site."""
    insights = []

    # Health index insights
    if site_data['health_index'] < HEALTH_CONFIG['health_thresholds']['critical']:
        insights.append({
            'type': 'critical',
            'title': 'Critical Health Status',
            'message': f"The site's health index ({site_data['health_index']:.2f}) is critically low. Immediate intervention is required."
        })
    elif site_data['health_index'] < HEALTH_CONFIG['health_thresholds']['warning']:
        insights.append({
            'type': 'warning',
            'title': 'Health Warning',
            'message': f"The site's health index ({site_data['health_index']:.2f}) is below the warning threshold. Regular monitoring is advised."
        })

    # Risk level insights
    if site_data['risk_level'] in ['High', 'Critical']:
        insights.append({
            'type': 'warning',
            'title': 'High Risk Level',
            'message': f"The site is classified as {site_data['risk_level']} risk. Enhanced preservation measures are recommended."
        })

    # Art forms insights
    endangered_art_forms = art_forms[art_forms['risk_level'].isin(['High', 'Critical'])]
    if not endangered_art_forms.empty:
        insights.append({
            'type': 'warning',
            'title': 'Endangered Art Forms',
            'message': f"The site hosts {len(endangered_art_forms)} endangered art forms that require immediate attention."
        })

    # Health trends insights
    if not health_trends.empty:
        recent_trend = health_trends.iloc[-1]['health_index'] - health_trends.iloc[0]['health_index']
        if recent_trend < -0.1:
            insights.append({
                'type': 'warning',
                'title': 'Declining Health',
                'message': "The site's health index has shown a significant decline in recent monitoring periods."
            })
        elif recent_trend > 0.1:
            insights.append({
                'type': 'success',
                'title': 'Improving Health',
                'message': "The site's health index has shown positive improvement in recent monitoring periods."
            })

    return insights

def render_heritage_health():
    """Render the heritage health page."""
    st.title("Heritage Health")
    st.markdown("Monitor and analyze the preservation status of heritage sites")

    # Get all heritage sites
    sites_df = get_heritage_sites()

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "Health Overview",
        "Site Analysis",
        "Preservation Insights"
    ])

    with tab1:
        st.subheader("Heritage Health Overview")

        # Health index distribution
        fig = px.histogram(
            sites_df,
            x='health_index',
            color='risk_level',
            title='Distribution of Health Indices',
            labels={'health_index': 'Health Index', 'count': 'Number of Sites'},
            color_discrete_map={
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red',
                'Critical': 'darkred'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        # Risk level distribution
        risk_counts = sites_df['risk_level'].value_counts()
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title='Distribution of Risk Levels',
            color=risk_counts.index,
            color_discrete_map={
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red',
                'Critical': 'darkred'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        # State-wise health metrics
        state_health = sites_df.groupby('state').agg({
            'health_index': 'mean',
            'site_id': 'count'
        }).reset_index()
        state_health.columns = ['state', 'avg_health_index', 'site_count']

        fig = px.bar(
            state_health,
            x='state',
            y='avg_health_index',
            color='site_count',
            title='Average Health Index by State',
            labels={
                'state': 'State',
                'avg_health_index': 'Average Health Index',
                'site_count': 'Number of Sites'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Site Health Analysis")

        # Site selection
        selected_site = st.selectbox(
            "Select Heritage Site",
            sites_df['name'].tolist()
        )

        if selected_site:
            # Get site data
            site_data = sites_df[sites_df['name'] == selected_site].iloc[0]

            # Get associated art forms and health trends
            art_forms = get_art_forms(site_data['site_id'])
            health_trends = get_health_trends(site_data['site_id'])

            # Display site metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Health Index",
                    f"{site_data['health_index']:.2f}",
                    delta=f"{health_trends.iloc[-1]['health_index'] - health_trends.iloc[0]['health_index']:.2f}" if not health_trends.empty else None
                )
            with col2:
                st.metric("Risk Level", site_data['risk_level'])
            with col3:
                st.metric(
                    "Preservation Score",
                    f"{calculate_preservation_score(site_data, art_forms):.1f}%"
                )

            # Health trends
            if not health_trends.empty:
                st.subheader("Health Trends")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=health_trends['visit_date'],
                    y=health_trends['health_index'],
                    name='Health Index',
                    line=dict(color='#1E88E5')
                ))
                fig.update_layout(
                    title='Health Index Trends',
                    xaxis_title='Date',
                    yaxis_title='Health Index',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Associated art forms
            if not art_forms.empty:
                st.subheader("Associated Art Forms")
                fig = px.bar(
                    art_forms,
                    x='name',
                    y='practitioners_count',
                    color='risk_level',
                    title='Art Forms by Risk Level',
                    labels={
                        'name': 'Art Form',
                        'practitioners_count': 'Number of Practitioners',
                        'risk_level': 'Risk Level'
                    },
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red',
                        'Critical': 'darkred'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Preservation Insights")

        # Site selection
        selected_site = st.selectbox(
            "Select Heritage Site for Insights",
            sites_df['name'].tolist(),
            key='insights_site'
        )

        if selected_site:
            # Get site data
            site_data = sites_df[sites_df['name'] == selected_site].iloc[0]

            # Get associated art forms and health trends
            art_forms = get_art_forms(site_data['site_id'])
            health_trends = get_health_trends(site_data['site_id'])

            # Generate insights
            insights = generate_preservation_insights(site_data, art_forms, health_trends)

            # Display insights
            for insight in insights:
                if insight['type'] == 'critical':
                    st.error(f"**{insight['title']}**\n{insight['message']}")
                elif insight['type'] == 'warning':
                    st.warning(f"**{insight['title']}**\n{insight['message']}")
                else:
                    st.success(f"**{insight['title']}**\n{insight['message']}")

            # Preservation recommendations
            st.subheader("Preservation Recommendations")

            # Health index recommendations
            if site_data['health_index'] < HEALTH_CONFIG['health_thresholds']['critical']:
                st.write("""
                ### Critical Health Recommendations:
                1. Conduct immediate structural assessment
                2. Implement emergency conservation measures
                3. Restrict visitor access if necessary
                4. Develop comprehensive restoration plan
                """)
            elif site_data['health_index'] < HEALTH_CONFIG['health_thresholds']['warning']:
                st.write("""
                ### Health Improvement Recommendations:
                1. Schedule regular maintenance
                2. Monitor environmental factors
                3. Implement preventive conservation measures
                4. Review visitor management policies
                """)

            # Art forms preservation recommendations
            endangered_art_forms = art_forms[art_forms['risk_level'].isin(['High', 'Critical'])]
            if not endangered_art_forms.empty:
                st.write("""
                ### Art Forms Preservation Recommendations:
                1. Document endangered art forms
                2. Support practitioner training programs
                3. Create digital archives
                4. Establish community engagement initiatives
                """)

            # General recommendations
            st.write("""
            ### General Preservation Guidelines:
            1. Regular monitoring and documentation
            2. Climate control and environmental management
            3. Visitor education and awareness programs
            4. Community involvement and stakeholder engagement
            5. Sustainable tourism practices
            """)
