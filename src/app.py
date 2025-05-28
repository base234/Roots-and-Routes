import streamlit as st
from src.components.dashboard import render_dashboard
from src.components.header import render_header
from src.components.footer import render_footer
from src.components.search_bar import render_search_bar
from src.components.featured_content import render_featured_content
from src.components.recommendations import render_recommendations
from src.components.trending import render_trending
from src.utils.database import get_db_connection
from src.utils.config import APP_CONFIG

# Load views
from src.views.metrics_overview import render_metrics_overview
from src.views.site_details import render_site_details
from src.views.tourism_analytics import render_tourism_analytics
from src.views.heritage_sites import render_heritage_sites_page
from src.views.cultural_events import render_cultural_events_page
from src.views.art_forms import render_art_forms_page

# Set page configuration
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar content (full length, options below heading)
st.sidebar.title(APP_CONFIG["title"])

# Database Connection Status
conn = get_db_connection()
if conn is not None:
    st.sidebar.markdown(
        '<div style="background-color:#e8f5e9;padding:2px 0;border-radius:6px;margin-bottom:10px;">'
        '<span style="color:#388e3c;font-size:14px;">🟢 DB Status: Connected</span>'
        '</div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<div style="background-color:#ffebee;padding:2px 0;border-radius:6px;margin-bottom:10px;">'
        '<span style="color:#c62828;font-size:14px;">🔴 DB Status: Disconnected</span>'
        '</div>',
        unsafe_allow_html=True
    )

# Initialize session state for navigation
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home'

# Navigation buttons in sidebar
if st.sidebar.button("Home", key="home_button"):
    st.session_state['current_view'] = 'home'
if st.sidebar.button("Metrics Overview", key="metrics_overview_button"):
    st.session_state['current_view'] = 'metrics_overview'
if st.sidebar.button("Discover", key="discover_button"):
    st.session_state['current_view'] = 'discover'
if st.sidebar.button("Tourism Analytics", key="tourism_analytics_button"):
    st.session_state['current_view'] = 'tourism_analytics'
if st.sidebar.button("AI Insights", key="ai_insights_button"):
    st.session_state['current_view'] = 'ai_insights'
if st.sidebar.button("Heritage Sites", key="heritage_sites_button"):
    st.session_state['current_view'] = 'heritage_sites'
if st.sidebar.button("Cultural Events", key="cultural_events_button"):
    st.session_state['current_view'] = 'cultural_events'
if st.sidebar.button("Art Forms", key="art_forms_button"):
    st.session_state['current_view'] = 'art_forms'

st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ for Cultural Heritage")

st.sidebar.markdown("""
    <div class="footer-links">
        <a href="#">About</a>
        <a href="#">Heritage Sites</a>
        <a href="#">Cultural Events</a>
        <a href="#">Art Forms</a>
        </div>
        <div class="footer-text">
            <p>&copy; 2025 Roots & Routes. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# Render content based on current view
current_view = st.session_state['current_view']

if current_view == 'home':
    st.markdown("## Trending Now")
    render_trending()
elif current_view == 'metrics_overview':
    st.markdown("## Metrics Overview")
    render_metrics_overview()
elif current_view == 'discover':
    st.markdown("## Discover World Heritage")
    st.markdown("<p style='font-size: 1.2rem; color: #666;'>Explore UNESCO World Heritage Sites and Cultural Treasures</p>", unsafe_allow_html=True)
    render_search_bar()
elif current_view == 'site_details':
    render_site_details()
elif current_view == 'tourism_analytics':
    st.markdown("## Tourism Analytics")
    render_tourism_analytics()
elif current_view == 'ai_insights':
    from src.views.ai_insights import render_ai_insights_page
    render_ai_insights_page()
elif current_view == 'heritage_sites':
    render_heritage_sites_page()
elif current_view == 'cultural_events':
    render_cultural_events_page()
elif current_view == 'art_forms':
    render_art_forms_page()

render_footer()
