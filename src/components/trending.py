import streamlit as st
from src.utils.database import get_trending_sites

def render_trending():
    """Render the trending heritage sites section."""
    # Get trending sites from database
    trending_sites = get_trending_sites(limit=4)

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
        </style>
    """, unsafe_allow_html=True)

    # Display trending sites in a horizontal layout
    cols = st.columns(4)

    for idx, site in enumerate(trending_sites):
        with cols[idx]:
            # Use a placeholder image if no image is available
            image_url = f"https://source.unsplash.com/featured/?{site['name']},heritage"
            st.image(image_url, use_container_width=True)
            st.markdown(f"#### {site['name']}")
            st.markdown(f"*{site['location']}, {site['state']}*")
            st.markdown(f"**Visitors:** {site['total_visitors']:,}")
            st.markdown(f"**Rating:** {site['avg_rating']:.1f} ⭐")
            st.button("Explore", key=f"trending_{idx}")
