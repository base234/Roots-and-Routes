import streamlit as st
from src.components.header import render_header
from src.components.footer import render_footer
from src.components.filters import render_filters
from src.components.map_view import render_map_view
from src.components.site_list import render_site_list
from src.components.pagination import render_pagination
from src.utils.database import get_heritage_sites

def render_explore_page():
    """Render the explore page with filters, map view, and site listings."""
    st.set_page_config(
        page_title="Explore Heritage Sites",
        page_icon="🗺️",
        layout="wide"
    )

    # Render header
    render_header()

    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>Explore Heritage Sites</h1>
            <p>Discover and filter through our collection of UNESCO World Heritage Sites</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")
        filters = render_filters()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Map view
        render_map_view()

        # Site listings
        st.markdown("### Heritage Sites")
        sites = get_heritage_sites(filters)
        render_site_list(sites)

        # Pagination
        render_pagination()

    with col2:
        # Additional information and statistics
        st.markdown("### Statistics")
        st.markdown("""
            - Total Sites: 1,154
            - Cultural Sites: 897
            - Natural Sites: 218
            - Mixed Sites: 39
        """)

        # Quick filters
        st.markdown("### Quick Filters")
        st.button("Most Visited")
        st.button("Recently Added")
        st.button("Endangered Sites")

    # Render footer
    render_footer()

if __name__ == "__main__":
    render_explore_page()
