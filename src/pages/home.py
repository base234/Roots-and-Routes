import streamlit as st
from src.components.header import render_header
from src.components.footer import render_footer
from src.components.search_bar import render_search_bar
from src.components.featured_content import render_featured_content
from src.components.recommendations import render_recommendations
from src.components.trending import render_trending

def render_home():
    """Render the home page."""
    render_header()

    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 1rem;'>Discover World Heritage</h1>
            <p style='font-size: 1.2rem; color: #666;'>Explore UNESCO World Heritage Sites and Cultural Treasures</p>
        </div>
    """, unsafe_allow_html=True)

    # Search bar
    render_search_bar()

    # Featured destinations
    st.markdown("## Featured Destinations")
    render_featured_content()

    # Trending now
    st.markdown("## Trending Now")
    render_trending()

    # Recommendations
    st.markdown("## Recommended for You")
    render_recommendations()

    render_footer()

if __name__ == "__main__":
    render_home()
