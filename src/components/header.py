import streamlit as st
from src.utils.config import APP_CONFIG, PAGES

def render_header():
    """Render the header with improved UI and navigation."""
    st.markdown("""
        <style>
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        .nav-item {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.1);
        }
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .nav-item.active {
            background: white;
            color: #1E88E5;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<h2>{APP_CONFIG["title"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p>{APP_CONFIG["description"]}</p>', unsafe_allow_html=True)

    # Navigation menu
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)

    # Get current page from session state or default to Home
    current_page = st.session_state.get('current_page', 'Home')

    for page, icon in PAGES.items():
        if st.button(f"{icon} {page}", key=f"nav_{page}"):
            st.session_state.current_page = page
            st.rerun()

    if st.button("Refresh", key="refresh_button"):
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
