import streamlit as st
from src.utils.database import get_related_sites, get_heritage_sites

def render_recommendations():
    """Render the recommendations section with AI-powered suggestions."""
    st.subheader("Recommended for You")

    # Get all sites and select a random one for recommendations
    all_sites = get_heritage_sites()
    if not all_sites:
        st.info("No recommendations available at the moment.")
        return

    # Use the first site as a reference point for recommendations
    reference_site = all_sites[0]
    recommended_sites = get_related_sites(reference_site['site_id'])

    if not recommended_sites:
        st.info("No recommendations available at the moment.")
        return

    # Display recommendations in three columns
    cols = st.columns(3)
    for idx, site in enumerate(recommended_sites[:3]):  # Limit to 3 sites here instead
        with cols[idx]:
            # Use a placeholder image if no image is available
            image_url = site.get('image_url', 'https://via.placeholder.com/300x200')
            st.image(image_url, use_container_width=True)
            st.markdown(f"### {site['name']}")
            st.markdown(f"**{site['location']}**")
            st.markdown(f"*{site['heritage_type']}*")
            st.markdown(f"Risk Level: {site['risk_level']}")
            st.button("View Details", key=f"rec_{idx}")
