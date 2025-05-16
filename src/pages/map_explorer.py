import streamlit as st
import pandas as pd
from components.map_view import render_map_view
from components.header import render_header
from components.footer import render_footer
from utils.database_config import snowflake_config

def render_map_explorer():
    """Render the map explorer page."""
    render_header()

    st.title("Heritage Sites Map Explorer")

    # Initialize Snowflake connection
    sf = snowflake_config

    # Get summary statistics
    query = """
    SELECT
        COUNT(*) as total_sites,
        COUNT(DISTINCT state) as total_states,
        COUNT(DISTINCT heritage_type) as total_types,
        AVG(average_rating) as avg_rating
    FROM site_analytics
    """
    stats = sf.execute_query(query)[0]

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sites", stats[0])
    with col2:
        st.metric("States Covered", stats[1])
    with col3:
        st.metric("Heritage Types", stats[2])
    with col4:
        st.metric("Average Rating", f"{stats[3]:.1f} ⭐")

    # Add tabs for different views
    tab1, tab2, tab3 = st.tabs(["Interactive Map", "State-wise View", "Heritage Type View"])

    with tab1:
        render_map_view()

    with tab2:
        st.subheader("State-wise Distribution")

        # Get state-wise statistics
        query = """
        SELECT
            state,
            COUNT(*) as site_count,
            SUM(total_visitors) as total_visitors,
            AVG(average_rating) as avg_rating
        FROM site_analytics
        GROUP BY state
        ORDER BY site_count DESC
        """
        state_stats = sf.execute_query(query)

        # Create state-wise metrics
        for state in state_stats:
            with st.expander(f"{state[0]} ({state[1]} sites)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Visitors", f"{state[2]:,}")
                with col2:
                    st.metric("Average Rating", f"{state[3]:.1f} ⭐")

    with tab3:
        st.subheader("Heritage Type Analysis")

        # Get heritage type statistics
        query = """
        SELECT
            heritage_type,
            COUNT(*) as site_count,
            SUM(total_visitors) as total_visitors,
            AVG(average_rating) as avg_rating
        FROM site_analytics
        GROUP BY heritage_type
        ORDER BY site_count DESC
        """
        type_stats = sf.execute_query(query)

        # Create heritage type metrics
        for heritage_type in type_stats:
            with st.expander(f"{heritage_type[0]} ({heritage_type[1]} sites)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Visitors", f"{heritage_type[2]:,}")
                with col2:
                    st.metric("Average Rating", f"{heritage_type[3]:.1f} ⭐")

    render_footer()

if __name__ == "__main__":
    render_map_explorer()
