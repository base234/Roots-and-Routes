import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import googlemaps
from utils.config import (
    GOOGLE_MAPS_API_KEY,
    MAPS_CONFIG
)
from utils.database import execute_query

def get_heritage_sites():
    """Fetch all heritage sites with their details."""
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

def create_base_map(center, zoom):
    """Create a base map centered on the specified location."""
    return folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )

def add_site_markers(map_obj, sites_df):
    """Add markers for heritage sites to the map."""
    for _, site in sites_df.iterrows():
        # Customize marker color based on risk level
        color = {
            'Low': 'green',
            'Medium': 'orange',
            'High': 'red',
            'Critical': 'darkred'
        }.get(site['risk_level'], 'blue')

        # Create popup content
        popup_content = f"""
        <b>{site['name']}</b><br>
        Type: {site['heritage_type']}<br>
        Location: {site['location']}, {site['state']}<br>
        Risk Level: {site['risk_level']}<br>
        Health Index: {site['health_index']:.2f}<br>
        Average Rating: {site['avg_rating']:.1f}/5.0
        """

        # Add marker
        folium.Marker(
            location=[site['latitude'], site['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(map_obj)

def calculate_route(origin, destination, waypoints=None):
    """Calculate route between points using Google Maps API."""
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

        # Prepare waypoints if provided
        if waypoints:
            waypoints = [f"via:{lat},{lng}" for lat, lng in waypoints]

        # Get directions
        directions = gmaps.directions(
            origin,
            destination,
            waypoints=waypoints,
            mode="driving",
            optimize_waypoints=True
        )

        if directions:
            return directions[0]
    except Exception as e:
        st.warning(f"Could not calculate route: {str(e)}")
    return None

def add_route_to_map(map_obj, route):
    """Add route to the map."""
    if not route:
        return

    # Extract route points
    points = []
    for leg in route['legs']:
        for step in leg['steps']:
            points.extend([
                [point['lat'], point['lng']]
                for point in step['polyline']['points']
            ])

    # Add route line
    folium.PolyLine(
        points,
        color='blue',
        weight=2,
        opacity=0.8
    ).add_to(map_obj)

def render_interactive_maps():
    """Render the interactive maps page."""
    st.title("Interactive Maps")
    st.markdown("Explore heritage sites and plan your cultural journey across India")

    # Get all heritage sites
    sites_df = get_heritage_sites()

    # Create tabs for different map views
    tab1, tab2 = st.tabs(["Heritage Sites Map", "Cultural Route Planner"])

    with tab1:
        st.subheader("Heritage Sites Map")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            selected_state = st.selectbox(
                "Filter by State",
                ["All"] + sorted(sites_df['state'].unique().tolist())
            )
        with col2:
            selected_type = st.selectbox(
                "Filter by Heritage Type",
                ["All"] + sorted(sites_df['heritage_type'].unique().tolist())
            )

        # Filter sites
        filtered_sites = sites_df.copy()
        if selected_state != "All":
            filtered_sites = filtered_sites[filtered_sites['state'] == selected_state]
        if selected_type != "All":
            filtered_sites = filtered_sites[filtered_sites['heritage_type'] == selected_type]

        # Create and display map
        m = create_base_map(
            MAPS_CONFIG['default_center'],
            MAPS_CONFIG['default_zoom']
        )
        add_site_markers(m, filtered_sites)
        folium_static(m, width=800, height=600)

        # Display site details
        if not filtered_sites.empty:
            st.subheader("Site Details")
            for _, site in filtered_sites.iterrows():
                with st.expander(site['name']):
                    st.write(site['description'])
                    st.write(f"Location: {site['location']}, {site['state']}")
                    st.write(f"Type: {site['heritage_type']}")
                    st.write(f"Risk Level: {site['risk_level']}")
                    st.write(f"Health Index: {site['health_index']:.2f}")

                    # Display associated art forms
                    art_forms = get_art_forms(site['site_id'])
                    if not art_forms.empty:
                        st.write("Associated Art Forms:")
                        for _, art_form in art_forms.iterrows():
                            st.write(f"- {art_form['name']}: {art_form['description']}")

    with tab2:
        st.subheader("Cultural Route Planner")

        # Route planning interface
        col1, col2 = st.columns(2)
        with col1:
            origin = st.selectbox(
                "Starting Point",
                sites_df['name'].tolist()
            )
        with col2:
            destination = st.selectbox(
                "Destination",
                sites_df['name'].tolist()
            )

        # Waypoints
        st.write("Add Waypoints (Optional)")
        waypoints = []
        num_waypoints = st.number_input("Number of Waypoints", 0, 5, 0)

        for i in range(num_waypoints):
            waypoint = st.selectbox(
                f"Waypoint {i+1}",
                sites_df['name'].tolist(),
                key=f"waypoint_{i}"
            )
            if waypoint:
                site = sites_df[sites_df['name'] == waypoint].iloc[0]
                waypoints.append((site['latitude'], site['longitude']))

        # Calculate and display route
        if st.button("Plan Route"):
            origin_site = sites_df[sites_df['name'] == origin].iloc[0]
            dest_site = sites_df[sites_df['name'] == destination].iloc[0]

            route = calculate_route(
                (origin_site['latitude'], origin_site['longitude']),
                (dest_site['latitude'], dest_site['longitude']),
                waypoints
            )

            if route:
                # Create route map
                m = create_base_map(
                    MAPS_CONFIG['default_center'],
                    MAPS_CONFIG['default_zoom']
                )

                # Add markers for all points
                add_site_markers(m, sites_df)

                # Add route
                add_route_to_map(m, route)

                # Display map
                folium_static(m, width=800, height=600)

                # Display route details
                st.subheader("Route Details")
                total_distance = sum(leg['distance']['value'] for leg in route['legs'])
                total_duration = sum(leg['duration']['value'] for leg in route['legs'])

                st.write(f"Total Distance: {total_distance/1000:.1f} km")
                st.write(f"Estimated Duration: {total_duration/3600:.1f} hours")

                # Display step-by-step directions
                st.subheader("Directions")
                for i, leg in enumerate(route['legs']):
                    st.write(f"Leg {i+1}:")
                    for step in leg['steps']:
                        st.write(f"- {step['html_instructions']}")
            else:
                st.error("Could not calculate route. Please try different locations.")
