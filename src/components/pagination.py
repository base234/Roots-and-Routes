import streamlit as st

def render_pagination(current_page=1, total_pages=10):
    """Render the pagination component."""
    st.markdown("""
        <style>
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        .page-link {
            padding: 0.5rem 1rem;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
            color: #007bff;
            text-decoration: none;
        }
        .page-link:hover {
            background-color: #e9ecef;
        }
        .page-link.active {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create columns for pagination controls
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if current_page > 1:
            st.button("Previous", key="prev_page")

    with col2:
        # Show page numbers
        st.markdown(f"Page {current_page} of {total_pages}")

    with col3:
        if current_page < total_pages:
            st.button("Next", key="next_page")

    # Store current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = current_page
