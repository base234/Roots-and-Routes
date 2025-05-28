import streamlit as st
from src.utils.database import get_all_heritage_sites
from src.utils.config import UNSPLASH_ACCESS_KEY
import requests

def get_site_image(site_name):
    """Fetch a relevant image for the heritage site from Unsplash."""
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{site_name}",
                "per_page": 1
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
        )
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    except Exception as e:
        st.warning(f"Could not fetch image: {str(e)}")
    return None

def render_heritage_sites_page():
    """Render the heritage sites page with all available sites."""
    # Add custom CSS for fixed image sizes
    st.markdown("""
        <style>
        div[data-testid="stImage"] {
            width: 100%;
            height: 200px;
            object-fit: cover;
            margin: 0;
        }
        div[data-testid="stImage"] img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## Heritage Sites")

    # Get all heritage sites
    sites = get_all_heritage_sites()

    if not sites:
        st.info("No heritage sites available at the moment.")
        return

    # Get unique states for the filter
    states = sorted(list(set(site['state'] for site in sites)))
    states.insert(0, "All States")  # Add "All States" as the first option

    # Create two columns for filters
    col1, col2 = st.columns(2)

    # Add state filter in first column
    with col1:
        selected_state = st.selectbox(
            "Filter by State",
            states,
            index=0
        )

    # Add UNESCO status filter in second column
    with col2:
        unesco_filter = st.radio(
            "UNESCO Status",
            ["All Sites", "UNESCO Sites", "Non-UNESCO Sites"],
            horizontal=True
        )

    # Filter sites by selected state
    if selected_state != "All States":
        sites = [site for site in sites if site['state'] == selected_state]

    # Filter sites by UNESCO status
    if unesco_filter == "UNESCO Sites":
        sites = [site for site in sites if site['unesco_status']]
    elif unesco_filter == "Non-UNESCO Sites":
        sites = [site for site in sites if not site['unesco_status']]

    # Show count of sites found
    if selected_state == "All States":
        st.markdown(f"Found {len(sites)} heritage sites across India")
    else:
        st.markdown(f"Found {len(sites)} heritage sites in {selected_state}")

    # Display sites in rows of 4
    for i in range(0, len(sites), 4):
        # Create a row of 4 columns
        cols = st.columns(4)

        # Fill each column with a site
        for j in range(4):
            if i + j < len(sites):
                site = sites[i + j]
                with cols[j]:
                    # Get site image
                    image_url = get_site_image(site['name'])
                    if not image_url:
                        image_url = "https://via.placeholder.com/400x200?text=No+Image+Available"

                    # Display site image
                    st.image(image_url, use_container_width=True)

                    # Display site information
                    st.markdown(f"**{site['name']}**")
                    st.markdown(f"*{site['location']}, {site['state']}*")

                    # Display UNESCO tag if applicable
                    if site.get('unesco_status'):
                        st.markdown(
                            '<div style="color: #1E88E5; display: inline-block;">'
                            '🏛️ UNESCO World Heritage Site'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div style="color: #FF6B00; display: inline-block;">'
                            '🏛️ Non-UNESCO World Heritage Site'
                            '</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(" ")
                    st.markdown(" ")

                    # Add view details button
                    if st.button("View Details", key=f"view_{site['name']}"):
                        st.session_state['selected_site'] = site['name']
                        st.session_state['current_view'] = 'site_details'
                        st.rerun()
        st.markdown(" ")
