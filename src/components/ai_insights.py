import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from typing import Dict

def render_health_score(health_data: dict):
    """Render the Cultural Heritage Health Score visualization"""
    st.subheader("Cultural Heritage Health Score")

    # Create radar chart for health scores
    categories = ['Physical Condition', 'Cultural Significance',
                 'Tourism Impact', 'Community Engagement']
    values = [
        health_data['physical_condition_score'],
        health_data['cultural_significance_score'],
        health_data['tourism_impact_score'],
        health_data['community_engagement_score']
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Health Score'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False
    )

    st.plotly_chart(fig)

    # Display overall score
    st.metric("Overall Health Score",
              f"{health_data['overall_health_score']:.2f}",
              delta=None)

def render_tourism_potential(potential_data: dict):
    """Render the Tourism Potential Index visualization"""
    st.subheader("Tourism Potential Analysis")

    # Create bar chart for potential scores
    categories = ['Visitor Score', 'Site Significance',
                 'Infrastructure', 'Community Capacity',
                 'Preservation Needs']
    values = [
        potential_data['current_visitor_score'],
        potential_data['site_significance_score'],
        potential_data['infrastructure_readiness'],
        potential_data['community_capacity'],
        potential_data['preservation_needs']
    ]

    fig = px.bar(
        x=categories,
        y=values,
        title="Tourism Potential Components",
        labels={'x': 'Component', 'y': 'Score'}
    )

    st.plotly_chart(fig)

    # Display overall potential score
    st.metric("Overall Tourism Potential",
              f"{potential_data['overall_potential_score']:.2f}",
              delta=None)

def render_seasonality_analysis(seasonality_data: Dict):
    """Render seasonality analysis section"""
    st.subheader("Tourism Seasonality Analysis")

    # Create a DataFrame for visualization
    seasons = list(seasonality_data['seasonal_patterns'].keys())
    values = list(seasonality_data['seasonal_patterns'].values())

    df = pd.DataFrame({
        'Season': seasons,
        'Visitor Index': values
    })

    # Create the line chart
    fig = px.line(
        df,
        x='Season',
        y='Visitor Index',
        title='Seasonal Visitor Patterns',
        labels={'Visitor Index': 'Normalized Visitor Count'},
        markers=True
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Season',
        yaxis_title='Normalized Visitor Count',
        yaxis_range=[0, 1],
        showlegend=False
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Display peak seasons
    st.write("Peak Seasons:", ", ".join(seasonality_data['peak_seasons']))

    # Display revenue opportunities
    st.write("Revenue Optimization Opportunities:")
    for opportunity in seasonality_data['revenue_opportunities']:
        st.write(f"- {opportunity}")

def render_preservation_priorities(priority_data: dict):
    """Render the preservation priorities visualization"""
    st.subheader("Preservation Priorities")

    # Create gauge chart for risk assessment
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=priority_data['risk_assessment_score'],
        title={'text': "Risk Assessment Score"},
        gauge={'axis': {'range': [0, 1]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 0.3], 'color': "lightgray"},
                   {'range': [0.3, 0.7], 'color': "gray"},
                   {'range': [0.7, 1], 'color': "darkgray"}
               ]}
    ))

    st.plotly_chart(fig)

    # Display priority level
    st.metric("Resource Allocation Priority",
              f"Level {priority_data['resource_allocation_priority']}")

    # Display implementation timeline
    st.write("Implementation Timeline:")
    for phase in priority_data['implementation_timeline']:
        st.write(f"- {phase}")

def render_ai_insights(site_id: int, ai_analysis):
    """Main function to render all AI insights"""
    st.title("AI-Powered Heritage Site Insights")

    # Get analysis data
    health_data = ai_analysis.calculate_health_score(site_id)
    potential_data = ai_analysis.calculate_tourism_potential(site_id)
    seasonality_data = ai_analysis.analyze_seasonality(site_id)
    priority_data = ai_analysis.generate_preservation_priorities(site_id)

    # Create tabs for different insights
    tab1, tab2, tab3, tab4 = st.tabs([
        "Health Score",
        "Tourism Potential",
        "Seasonality",
        "Preservation"
    ])

    with tab1:
        render_health_score(health_data)

    with tab2:
        render_tourism_potential(potential_data)

    with tab3:
        render_seasonality_analysis(seasonality_data)

    with tab4:
        render_preservation_priorities(priority_data)
