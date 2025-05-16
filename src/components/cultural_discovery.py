import streamlit as st
import pandas as pd
import plotly.express as px
import googlemaps
from PIL import Image
import requests
from io import BytesIO
from utils.config import (
    DISCOVERY_CONFIG,
    GOOGLE_MAPS_API_KEY,
    UNSPLASH_API_KEY
)
from utils.database import execute_query

def get_heritage_sites(search_query=None, state=None, heritage_type=None, risk_level=None):
    """Fetch heritage sites with filters."""
    query = """
    SELECT
        h.*,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND (LOWER(h.name) LIKE LOWER(%s) OR LOWER(h.description) LIKE LOWER(%s))"
        search_param = f"%{search_query}%"
        params.extend([search_param, search_param])

    if state:
        query += " AND h.state = %s"
        params.append(state)

    if heritage_type:
        query += " AND h.heritage_type = %s"
        params.append(heritage_type)

    if risk_level:
        query += " AND h.risk_level = %s"
        params.append(risk_level)

    query += """
    GROUP BY h.site_id, h.name, h.description, h.location, h.latitude, h.longitude,
             h.state, h.city, h.established_year, h.heritage_type, h.unesco_status,
             h.risk_level, h.health_index
    ORDER BY total_visitors DESC, avg_rating DESC
    LIMIT %s
    """
    params.append(DISCOVERY_CONFIG['search_limit'])

    return execute_query(query, params)

def get_art_forms(site_id):
    """Fetch art forms associated with a heritage site."""
    query = """
    SELECT a.*
    FROM ART_FORMS a
    JOIN SITE_ART_FORMS sa ON a.art_form_id = sa.art_form_id
    WHERE sa.site_id = %s
    """
    return execute_query(query, [site_id])

def get_site_image(site_name):
    """Fetch a relevant image for the heritage site from Unsplash."""
    try:
        response = requests.get(
            f"https://api.unsplash.com/search/photos",
            params={
                "query": f"{site_name} india heritage",
                "per_page": 1
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_API_KEY}"
            }
        )
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    except Exception as e:
        st.warning(f"Could not fetch image: {str(e)}")
    return None

def get_street_view(latitude, longitude):
    """Get Google Street View image for a location."""
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        street_view = gmaps.streetview(
            location=(latitude, longitude),
            size=(600, 400),
            heading=0,
            pitch=0
        )
        return street_view
    except Exception as e:
        st.warning(f"Could not fetch street view: {str(e)}")
    return None

def generate_ai_description(site_data):
    """Generate an AI-powered description for the heritage site."""
    # This is a placeholder for actual AI integration
    # In a real implementation, this would call an AI service
    description = f"""
    {site_data['name']} is a remarkable {site_data['heritage_type'].lower()} located in {site_data['city']}, {site_data['state']}.
    Established in {site_data['established_year']}, this site represents a significant part of India's cultural heritage.

    The site's current health index of {site_data['health_index']:.2f} indicates its preservation status,
    while the {site_data['risk_level'].lower()} risk level suggests the level of attention needed for its conservation.

    With an average visitor rating of {site_data['avg_rating']:.1f}/5.0, it continues to be a popular destination
    for those interested in exploring India's rich cultural heritage.
    """
    return description

def render_cultural_discovery():
    """Render the cultural discovery page."""
    st.title("Cultural Discovery")
    st.markdown("Explore India's rich cultural heritage through our interactive discovery platform")

    # Search and Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_query = st.text_input("Search Heritage Sites", "")

    with col2:
        state = st.selectbox(
            "State",
            ["All"] + sorted(execute_query("SELECT DISTINCT state FROM HERITAGE_SITES")['state'].tolist())
        )
        if state == "All":
            state = None

    with col3:
        heritage_type = st.selectbox(
            "Heritage Type",
            ["All"] + DISCOVERY_CONFIG['filter_options']['heritage_types']
        )
        if heritage_type == "All":
            heritage_type = None

    with col4:
        risk_level = st.selectbox(
            "Risk Level",
            ["All"] + DISCOVERY_CONFIG['filter_options']['risk_levels']
        )
        if risk_level == "All":
            risk_level = None

    # Fetch and display results
    sites = get_heritage_sites(search_query, state, heritage_type, risk_level)

    if sites.empty:
        st.info("No heritage sites found matching your criteria.")
        return

    # Display results in a grid
    for _, site in sites.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 2])

            with col1:
                # Display site image
                image_url = get_site_image(site['name'])
                if image_url:
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content))
                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        st.image("assets/placeholder.jpg", use_container_width=True)
                else:
                    st.image("assets/placeholder.jpg", use_container_width=True)

            with col2:
                st.subheader(site['name'])

                # Display AI-generated description
                st.markdown(generate_ai_description(site))

                # Display key metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric("Health Index", f"{site['health_index']:.2f}")
                with metrics_col2:
                    st.metric("Risk Level", site['risk_level'])
                with metrics_col3:
                    st.metric("Average Rating", f"{site['avg_rating']:.1f}/5.0")

                # Display associated art forms
                art_forms = get_art_forms(site['site_id'])
                if not art_forms.empty:
                    st.subheader("Associated Art Forms")
                    for _, art_form in art_forms.iterrows():
                        st.markdown(f"- **{art_form['name']}**: {art_form['description']}")

                # Display Google Street View
                if st.button(f"View {site['name']} on Street View", key=f"street_view_{site['site_id']}"):
                    street_view = get_street_view(site['latitude'], site['longitude'])
                    if street_view:
                        st.image(street_view, use_container_width=True)
                    else:
                        st.warning("Street view not available for this location.")

            st.markdown("---")
