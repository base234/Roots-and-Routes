import streamlit as st
from src.components.header import render_header
from src.components.footer import render_footer
from src.components.image_gallery import render_image_gallery
from src.components.reviews import render_reviews
from src.components.related_sites import render_related_sites
from src.components.visit_info import render_visit_info
from src.utils.database import get_site_details

def render_site_details_page(site_id):
    """Render the detailed view of a heritage site."""
    st.set_page_config(
        page_title="Site Details",
        page_icon="🏛️",
        layout="wide"
    )

    # Get site details
    site = get_site_details(site_id)

    # Render header
    render_header()

    # Site title and basic info
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>{site['name']}</h1>
            <p>{site['location']} • {site['category']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Image gallery
        render_image_gallery(site['images'])

        # Description
        st.markdown("### About")
        st.markdown(site['description'])

        # Historical significance
        st.markdown("### Historical Significance")
        st.markdown(site['historical_significance'])

        # Conservation status
        st.markdown("### Conservation Status")
        st.markdown(site['conservation_status'])

        # Reviews
        st.markdown("### Visitor Reviews")
        render_reviews(site_id)

    with col2:
        # Visit information
        render_visit_info(site)

        # Quick facts
        st.markdown("### Quick Facts")
        st.markdown(f"""
            - Year of Inscription: {site['inscription_year']}
            - Criteria: {site['criteria']}
            - Area: {site['area']}
            - Buffer Zone: {site['buffer_zone']}
        """)

        # Related sites
        st.markdown("### Related Sites")
        render_related_sites(site['related_sites'])

        # Share buttons
        st.markdown("### Share")
        st.button("Share on Facebook")
        st.button("Share on Twitter")
        st.button("Share via Email")

    # Render footer
    render_footer()

if __name__ == "__main__":
    # For testing, use a sample site ID
    render_site_details_page("sample_site_id")
