import streamlit as st
from src.utils.database import get_trending_sites
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

def render_trending():
    """Render the trending heritage sites section."""
    # Get trending sites from database
    trending_sites = get_trending_sites(limit=8)

    if not trending_sites:
        st.info("No trending sites available at the moment.")
        return

    # Create a horizontal scrollable container
    st.markdown("""
        <style>
        .trending-container {
            display: flex;
            overflow-x: auto;
            gap: 1rem;
            padding: 1rem 0;
        }
        .trending-item {
            flex: 0 0 auto;
            width: 250px;
        }
        .read-more-link {
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }
        .read-more-link:hover {
            text-decoration: underline;
        }
        .trending-image {
            width: 250px;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display trending sites in two rows of 4 columns each
    num_cols = 4
    for row in range(2):  # Two rows
        cols = st.columns(num_cols)
        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < len(trending_sites):
                with cols[col]:
                    site = trending_sites[idx]
                    # Use Unsplash API to get a relevant image
                    image_url = get_site_image(site['name'])
                    if image_url:
                        st.markdown(f'<img src="{image_url}" class="trending-image">', unsafe_allow_html=True)
                    else:
                        st.markdown('<img src="https://via.placeholder.com/400x300?text=No+Image+Available" class="trending-image">', unsafe_allow_html=True)
                    st.markdown(f"#### {site['name']}")
                    st.markdown(f"*{site['location']}, {site['state']}*")
                    st.markdown(f"**Visitors:** {site['total_visitors']:,}")
                    st.markdown(f"**Rating:** {site['avg_rating']:.1f} ⭐")
                    # Add Read More link
                    if st.button(f"Read More about {site['name']}", key=f"read_more_{site['name']}"):
                        st.session_state['selected_site'] = site['name']
                        st.session_state['current_view'] = 'site_details'
                        st.rerun()
