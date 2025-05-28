import streamlit as st
import pandas as pd
from src.services.ai_analysis import HeritageAIAnalysis
from src.components.ai_insights import (
    render_health_score,
    render_tourism_potential,
    render_seasonality_analysis,
    render_preservation_priorities
)
from src.utils.database import get_db_connection

def get_heritage_sites():
    """Get list of heritage sites with visitor counts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First, let's check what tables exist in the current schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = current_schema()
        """)
        tables = cursor.fetchall()
        print("Available tables:", [table[0] for table in tables])

        # Let's check the current schema
        cursor.execute("SELECT current_schema()")
        current_schema = cursor.fetchone()[0]
        print("Current schema:", current_schema)

        # Now let's check the columns in HERITAGE_SITES
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
            AND table_name = 'HERITAGE_SITES'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("HERITAGE_SITES columns:", [col[0] for col in columns])

        # Let's try a query with the actual column names
        if columns:
            column_names = [col[0] for col in columns]
            id_col = next((col for col in column_names if col.upper() in ['ID', 'SITE_ID', 'HERITAGE_ID']), None)
            name_col = next((col for col in column_names if col.upper() in ['NAME', 'SITE_NAME', 'HERITAGE_NAME']), None)
            location_col = next((col for col in column_names if col.upper() in ['LOCATION', 'SITE_LOCATION']), None)
            state_col = next((col for col in column_names if col.upper() in ['STATE', 'SITE_STATE']), None)

            if all([id_col, name_col, location_col, state_col]):
                query = f"""
                    SELECT
                        "{id_col}",
                        "{name_col}",
                        "{location_col}",
                        "{state_col}"
                    FROM "{current_schema}"."HERITAGE_SITES"
                    ORDER BY "{name_col}"
                """
                print("Executing query:", query)
                cursor.execute(query)
                sites = cursor.fetchall()

                # Create DataFrame with basic site info
                df = pd.DataFrame(sites, columns=['ID', 'Name', 'Location', 'State'])

                # Add visitor stats if available
                try:
                    cursor.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = current_schema()
                        AND table_name = 'VISITOR_STATS'
                        ORDER BY ordinal_position
                    """)
                    visitor_columns = cursor.fetchall()
                    print("VISITOR_STATS columns:", [col[0] for col in visitor_columns])

                    if visitor_columns:
                        visitor_cols = [col[0] for col in visitor_columns]
                        site_id_col = next((col for col in visitor_cols if col.upper() in ['SITE_ID', 'HERITAGE_ID']), None)
                        visitor_count_col = next((col for col in visitor_cols if col.upper() in ['VISITOR_COUNT', 'COUNT', 'TOTAL_VISITORS']), None)

                        if site_id_col and visitor_count_col:
                            visitor_query = f"""
                                SELECT
                                    "{site_id_col}",
                                    COUNT(*) as visitor_count,
                                    AVG("{visitor_count_col}") as avg_visitors
                                FROM "{current_schema}"."VISITOR_STATS"
                                GROUP BY "{site_id_col}"
                            """
                            print("Executing visitor query:", visitor_query)
                            cursor.execute(visitor_query)
                            visitor_stats = cursor.fetchall()
                            visitor_df = pd.DataFrame(visitor_stats, columns=['ID', 'Total Visits', 'Average Visitors'])

                            # Merge visitor stats with site info
                            df = df.merge(visitor_df, on='ID', how='left')
                            df['Total Visits'] = df['Total Visits'].fillna(0)
                            df['Average Visitors'] = df['Average Visitors'].fillna(0)
                except Exception as e:
                    print("Error getting visitor stats:", str(e))
                    df['Total Visits'] = 0
                    df['Average Visitors'] = 0

                return df
            else:
                print("Could not find all required columns in HERITAGE_SITES")
                return pd.DataFrame(columns=['ID', 'Name', 'Location', 'State', 'Total Visits', 'Average Visitors'])
        else:
            print("No columns found in HERITAGE_SITES table")
            return pd.DataFrame(columns=['ID', 'Name', 'Location', 'State', 'Total Visits', 'Average Visitors'])

    finally:
        cursor.close()
        conn.close()

def get_site_observations(site_data, health_data, potential_data, seasonality_data, priority_data):
    """Generate observations and recommendations for a site"""
    observations = []

    # Check visitor patterns
    if site_data['Average Visitors'] < 100:
        observations.append({
            'issue': 'Low Visitor Count',
            'reason': 'The site has significantly lower visitor numbers compared to other heritage sites.',
            'solution': 'Consider implementing targeted marketing campaigns and improving accessibility.'
        })

    # Check health score
    if health_data['overall_health_score'] < 0.5:
        observations.append({
            'issue': 'Poor Health Score',
            'reason': 'The site shows signs of deterioration or lack of maintenance.',
            'solution': 'Prioritize preservation efforts and regular maintenance schedules.'
        })

    # Check tourism potential
    if potential_data['overall_potential_score'] < 0.4:
        observations.append({
            'issue': 'Low Tourism Potential',
            'reason': 'The site has untapped potential for tourism development.',
            'solution': 'Develop infrastructure and create unique visitor experiences.'
        })

    # Check seasonality
    if len(seasonality_data['peak_seasons']) < 2:
        observations.append({
            'issue': 'Limited Peak Seasons',
            'reason': 'Visitor numbers are concentrated in few seasons.',
            'solution': 'Create off-season attractions and promotional activities.'
        })

    # Check preservation needs
    if priority_data['risk_assessment_score'] > 0.7:
        observations.append({
            'issue': 'High Preservation Risk',
            'reason': 'The site requires immediate attention for preservation.',
            'solution': 'Implement emergency preservation measures and secure funding.'
        })

    return observations

def render_heritage_sites_list():
    """Render the heritage sites list tab"""
    st.subheader("Heritage Sites by Visitor Count")

    # Get sites data
    sites_df = get_heritage_sites()

    # Add radio buttons for sorting
    sort_order = st.radio(
        "Sort by Visitor Count",
        ["Low to High", "High to Low"],
        horizontal=True,
        index=0
    )

    # Sort the dataframe
    if sort_order == "High to Low":
        sites_df = sites_df.sort_values('Average Visitors', ascending=False)
    else:
        sites_df = sites_df.sort_values('Average Visitors', ascending=True)

    # Display the table
    st.dataframe(
        sites_df,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Name": st.column_config.TextColumn("Name", width="large"),
            "Location": st.column_config.TextColumn("Location", width="medium"),
            "State": st.column_config.TextColumn("State", width="small"),
            "Total Visits": st.column_config.NumberColumn("Total Visits", width="medium"),
            "Average Visitors": st.column_config.NumberColumn("Average Visitors", width="medium", format="%.2f")
        },
        hide_index=True
    )

def render_site_insights():
    """Render the site insights tab"""
    st.subheader("Site Insights")

    # Get sites for dropdown
    sites_df = get_heritage_sites()
    site_names = sites_df['Name'].tolist()

    # Site selection
    selected_site = st.selectbox("Select Heritage Site", site_names)

    if selected_site:
        # Get site ID
        site_id = sites_df[sites_df['Name'] == selected_site]['ID'].iloc[0]

        # Initialize AI analysis
        conn = get_db_connection()
        ai_analysis = HeritageAIAnalysis(conn)

        try:
            # Get all analysis data
            health_data = ai_analysis.calculate_health_score(site_id)
            potential_data = ai_analysis.calculate_tourism_potential(site_id)
            seasonality_data = ai_analysis.analyze_seasonality(site_id)
            priority_data = ai_analysis.generate_preservation_priorities(site_id)
            site_data = sites_df[sites_df['ID'] == site_id].iloc[0].to_dict()

            # Create tabs for different insights
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Health Score",
                "Tourism Potential",
                "Seasonality",
                "Preservation",
                "Observations"
            ])

            with tab1:
                render_health_score(health_data)

            with tab2:
                render_tourism_potential(potential_data)

            with tab3:
                render_seasonality_analysis(seasonality_data)

            with tab4:
                render_preservation_priorities(priority_data)

            with tab5:
                st.subheader("Site Observations and Recommendations")
                observations = get_site_observations(
                    site_data,
                    health_data,
                    potential_data,
                    seasonality_data,
                    priority_data
                )

                for obs in observations:
                    with st.expander(f"🔍 {obs['issue']}"):
                        st.write("**Reason:**")
                        st.write(obs['reason'])
                        st.write("**Recommended Solution:**")
                        st.write(obs['solution'])

        finally:
            conn.close()

def render_ai_insights_page():
    """Main function to render the AI insights page"""
    st.markdown("## Heritage Sites Analysis")

    # Create main tabs
    tab1, tab2 = st.tabs(["Heritage Sites List", "Site Insights"])

    with tab1:
        render_heritage_sites_list()

    with tab2:
        render_site_insights()

if __name__ == "__main__":
    render_ai_insights_page()
