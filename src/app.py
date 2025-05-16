import streamlit as st
from src.components.header import render_header
from src.components.footer import render_footer
from src.components.search_bar import render_search_bar
from src.components.featured_content import render_featured_content
from src.components.recommendations import render_recommendations
from src.components.trending import render_trending
from src.utils.database import get_db_connection

# Set page configuration
st.set_page_config(
    page_title="Roots and Routes",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar content (full length, options below heading)
st.sidebar.title("Roots and Routes")

# Database Connection Status
conn = get_db_connection()
if conn is not None:
    st.sidebar.markdown(
        '<div style="background-color:#e8f5e9;padding:10px;border-radius:6px;margin-bottom:10px;">'
        '<span style="color:#388e3c;font-weight:bold;">🟢 Database Connected</span>'
        '</div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<div style="background-color:#ffebee;padding:10px;border-radius:6px;margin-bottom:10px;">'
        '<span style="color:#c62828;font-weight:bold;">🔴 Database Disconnected</span>'
        '</div>',
        unsafe_allow_html=True
    )

# Use session state to track the current page
if 'sidebar_page' not in st.session_state:
    st.session_state['sidebar_page'] = 'Home'

if st.sidebar.button("Home", key="home_button"):
    st.session_state['sidebar_page'] = 'Home'
if st.sidebar.button("Featured Destinations", key="featured_button"):
    st.session_state['sidebar_page'] = 'Featured Destinations'
if st.sidebar.button("Trending Now", key="trending_button"):
    st.session_state['sidebar_page'] = 'Trending Now'
if st.sidebar.button("Recommended for You", key="recommended_button"):
    st.session_state['sidebar_page'] = 'Recommended for You'

st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ for Cultural Heritage")
st.sidebar.markdown("""
    <div class="footer-links">
        <a href="#">About</a>
        <a href="#">Heritage Sites</a>
        <a href="#">Cultural Events</a>
        </div>
        <div class="footer-text">
            <p>&copy; 2025 Roots & Routes. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# Render content based on sidebar selection
print("Current Page: " + st.session_state['sidebar_page'])
# render_header()

page = st.session_state['sidebar_page']

if page == "Home":
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 1rem;'>Discover World Heritage</h1>
            <p style='font-size: 1.2rem; color: #666;'>Explore UNESCO World Heritage Sites and Cultural Treasures</p>
        </div>
    """, unsafe_allow_html=True)
    render_search_bar()
    st.markdown("## Featured Destinations")
    render_featured_content()
    st.markdown("## Trending Now")
    render_trending()
    st.markdown("## Recommended for You")
    render_recommendations()
elif page == "Featured Destinations":
    st.markdown("## Featured Destinations")
    render_featured_content()
elif page == "Trending Now":
    st.markdown("## Trending Now")
    render_trending()
elif page == "Recommended for You":
    st.markdown("## Recommended for You")
    render_recommendations()

render_footer()
