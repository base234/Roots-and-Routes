import streamlit as st
import folium
from streamlit_folium import folium_static
from utils.database_config import snowflake_config

def render_map_view():
    """Render the interactive map view of heritage sites."""
    st.subheader("Heritage Sites Map")

    # Initialize Snowflake connection
    sf = snowflake_config

    # Get all heritage sites with their coordinates
    query = """
    SELECT
        name,
        location,
        state,
        heritage_type,
        latitude,
        longitude,
        total_visitors,
        average_rating
    FROM site_analytics
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    sites = sf.execute_query(query)

    if not sites:
        st.warning("No heritage sites found with location data.")
        return

    # Create a map centered on India
    m = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles='CartoDB positron'
    )

    # Add markers for each site
    for site in sites:
        name, location, state, heritage_type, lat, lon, visitors, rating = site

        # Create popup content
        popup_content = f"""
        <div style='width: 200px'>
            <h4>{name}</h4>
            <p><b>Location:</b> {location}, {state}</p>
            <p><b>Type:</b> {heritage_type}</p>
            <p><b>Visitors:</b> {visitors:,}</p>
            <p><b>Rating:</b> {rating:.1f} ⭐</p>
        </div>
        """

        # Create marker with custom icon
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=name,
            icon=folium.Icon(
                color='red' if heritage_type == 'UNESCO World Heritage Site' else 'blue',
                icon='info-sign'
            )
        ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Display the map
    folium_static(m, width=800, height=600)

    # Add filters
    st.sidebar.subheader("Map Filters")

    # Filter by heritage type
    heritage_types = list(set(site[3] for site in sites))
    selected_types = st.sidebar.multiselect(
        "Heritage Type",
        heritage_types,
        default=heritage_types
    )

    # Filter by state
    states = list(set(site[2] for site in sites))
    selected_states = st.sidebar.multiselect(
        "State",
        states,
        default=states
    )

    # Filter by visitor count
    min_visitors, max_visitors = st.sidebar.slider(
        "Visitor Count Range",
        min_value=0,
        max_value=max(site[6] for site in sites),
        value=(0, max(site[6] for site in sites))
    )

    # Filter by rating
    min_rating, max_rating = st.sidebar.slider(
        "Rating Range",
        min_value=0.0,
        max_value=5.0,
        value=(0.0, 5.0),
        step=0.1
    )

    # Apply filters
    filtered_sites = [
        site for site in sites
        if site[3] in selected_types
        and site[2] in selected_states
        and min_visitors <= site[6] <= max_visitors
        and min_rating <= site[7] <= max_rating
    ]

    # Display filtered sites count
    st.sidebar.info(f"Showing {len(filtered_sites)} of {len(sites)} sites")

    # Add site list below map
    if filtered_sites:
        st.subheader("Filtered Sites")
        for site in filtered_sites:
            with st.expander(f"{site[0]} - {site[1]}, {site[2]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Heritage Type:** {site[3]}")
                    st.write(f"**Total Visitors:** {site[6]:,}")
                with col2:
                    st.write(f"**Rating:** {site[7]:.1f} ⭐")
                    st.write(f"**Coordinates:** {site[4]:.4f}, {site[5]:.4f}")
