import streamlit as st
from src.utils.config import APP_CONFIG

def render_featured_content():
    """Render the featured content section with improved UI."""
    st.markdown("""
        <style>
        .featured-content {
            padding: 2rem 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
            border-radius: 15px;
            margin: 2rem 0;
        }
        .featured-title {
            color: #1E88E5;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .featured-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .featured-card:hover {
            transform: translateY(-5px);
        }
        .featured-card h3 {
            color: #1E88E5;
            margin-bottom: 1rem;
        }
        .featured-card p {
            color: #666;
            line-height: 1.6;
        }
        .featured-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="featured-card">
                <h3>🏛️ Taj Mahal</h3>
                <p>Experience the timeless beauty of India's most iconic monument.
                A UNESCO World Heritage site that stands as a testament to eternal love.</p>
                <p><strong>Best Time to Visit:</strong> October to March</p>
                <p><strong>Location:</strong> Agra, Uttar Pradesh</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="featured-card">
                <h3>🕌 Hampi</h3>
                <p>Explore the ruins of the magnificent Vijayanagara Empire.
                A treasure trove of ancient temples and architectural marvels.</p>
                <p><strong>Best Time to Visit:</strong> October to February</p>
                <p><strong>Location:</strong> Karnataka</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="featured-card">
                <h3>🏰 Khajuraho</h3>
                <p>Discover the stunning temples adorned with intricate sculptures.
                A UNESCO World Heritage site showcasing ancient Indian art.</p>
                <p><strong>Best Time to Visit:</strong> October to March</p>
                <p><strong>Location:</strong> Madhya Pradesh</p>
            </div>
        """, unsafe_allow_html=True)
