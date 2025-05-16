import streamlit as st
from src.utils.config import APP_CONFIG

def render_footer():
    """Render a professional footer with basic styles."""
    st.markdown("""
        <style>
        .footer {
            padding: 2rem 0;
            margin-top: 0rem;
            border-top: 1px solid #e0e0e0;
        }
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        .footer-links {
            font-size: 14px;
            margin: 0rem 0;
        }
        .footer-links a {
            color: #1E88E5;
            text-decoration: none;
            margin-right: 10px;
        }
        .footer-links a:hover {
            text-decoration: underline;
        }
        .footer-text {
            color: #666;
            font-size: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('<div class="footer-content">', unsafe_allow_html=True)

    # Main content
    st.markdown("""
        <div class="footer-links">
            <a href="#">About</a>
            <a href="#">Heritage Sites</a>
            <a href="#">Cultural Events</a>
            <a href="#">Contact</a>
        </div>
        <div class="footer-text">
            <p>Exploring and preserving India's rich cultural heritage through technology and tourism.</p>
            <p>© 2025 Roots & Routes. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
