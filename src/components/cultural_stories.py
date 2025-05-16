import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import execute_query
from utils.config import STORIES_CONFIG

def get_heritage_sites():
    """Fetch heritage sites with their details."""
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

def get_cultural_events(site_id):
    """Fetch cultural events associated with a heritage site."""
    query = """
    SELECT *
    FROM CULTURAL_EVENTS
    WHERE site_id = %s
    ORDER BY start_date DESC
    """
    return execute_query(query, [site_id])

def generate_story(site_data, art_forms, events, story_type):
    """Generate a cultural story based on site data and selected type."""
    # This is a placeholder for actual AI integration
    # In a real implementation, this would call an AI service

    if story_type == "Historical":
        story = f"""
        # The Legacy of {site_data['name']}

        In the heart of {site_data['city']}, {site_data['state']}, stands the magnificent {site_data['name']},
        a testament to India's rich cultural heritage. Established in {site_data['established_year']},
        this {site_data['heritage_type'].lower()} has witnessed centuries of history unfold.

        ## Historical Significance
        {site_data['description']}

        ## Cultural Heritage
        The site is home to several traditional art forms that have been preserved through generations:
        """
        for _, art_form in art_forms.iterrows():
            story += f"\n- **{art_form['name']}**: {art_form['description']}"

    elif story_type == "Contemporary":
        story = f"""
        # {site_data['name']} Today

        ## Modern Significance
        {site_data['name']} continues to be a vibrant center of cultural activity,
        attracting {site_data['total_visitors']:,} visitors annually. With an average rating of
        {site_data['avg_rating']:.1f}/5.0, it remains one of the most cherished heritage sites in India.

        ## Cultural Events
        The site hosts several cultural events throughout the year:
        """
        for _, event in events.iterrows():
            story += f"\n- **{event['name']}**: {event['description']}"

    elif story_type == "Preservation":
        story = f"""
        # Preserving {site_data['name']}

        ## Conservation Status
        With a health index of {site_data['health_index']:.2f} and a {site_data['risk_level'].lower()} risk level,
        {site_data['name']} requires careful attention to ensure its preservation for future generations.

        ## Associated Art Forms
        The site is home to several endangered art forms that need protection:
        """
        for _, art_form in art_forms.iterrows():
            story += f"\n- **{art_form['name']}**: {art_form['description']}\n  Risk Level: {art_form['risk_level']}"

    return story

def render_cultural_stories():
    """Render the cultural stories page."""
    st.title("Cultural Stories")
    st.markdown("Discover the rich narratives behind India's heritage sites")

    # Get all heritage sites
    sites_df = get_heritage_sites()

    # Create tabs for different story types
    tab1, tab2 = st.tabs(["Story Generator", "Featured Stories"])

    with tab1:
        st.subheader("Generate Your Story")

        # Site selection
        selected_site = st.selectbox(
            "Select Heritage Site",
            sites_df['name'].tolist()
        )

        if selected_site:
            # Get site data
            site_data = sites_df[sites_df['name'] == selected_site].iloc[0]

            # Get associated art forms and events
            art_forms = get_art_forms(site_data['site_id'])
            events = get_cultural_events(site_data['site_id'])

            # Story type selection
            story_type = st.radio(
                "Select Story Type",
                ["Historical", "Contemporary", "Preservation"]
            )

            # Generate and display story
            if st.button("Generate Story"):
                story = generate_story(site_data, art_forms, events, story_type)
                st.markdown(story)

                # Add download button
                st.download_button(
                    "Download Story",
                    story,
                    file_name=f"{selected_site.replace(' ', '_')}_{story_type.lower()}_story.md",
                    mime="text/markdown"
                )

    with tab2:
        st.subheader("Featured Stories")

        # Display featured sites
        featured_sites = sites_df.sort_values('total_visitors', ascending=False).head(3)

        for _, site in featured_sites.iterrows():
            with st.expander(site['name']):
                # Get associated art forms and events
                art_forms = get_art_forms(site['site_id'])
                events = get_cultural_events(site['site_id'])

                # Generate and display story
                story = generate_story(site, art_forms, events, "Historical")
                st.markdown(story)

                # Display key metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Visitors", f"{site['total_visitors']:,}")
                with col2:
                    st.metric("Average Rating", f"{site['avg_rating']:.1f}/5.0")
                with col3:
                    st.metric("Health Index", f"{site['health_index']:.2f}")

                # Display associated art forms
                if not art_forms.empty:
                    st.subheader("Associated Art Forms")
                    for _, art_form in art_forms.iterrows():
                        st.markdown(f"- **{art_form['name']}**: {art_form['description']}")

                # Display upcoming events
                if not events.empty:
                    st.subheader("Upcoming Events")
                    for _, event in events.iterrows():
                        st.markdown(f"- **{event['name']}**: {event['description']}")
                        st.markdown(f"  Date: {event['start_date']} to {event['end_date']}")
                        st.markdown(f"  Organizer: {event['organizer']}")
