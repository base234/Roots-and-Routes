import streamlit as st
from src.utils.database import get_site_details

def render_site_list(sites):
    """Render the list of heritage sites."""
    for site in sites:
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                # Site image (placeholder for now)
                st.image(
                    "https://via.placeholder.com/150",
                    width=150
                )

            with col2:
                # Site information
                st.markdown(f"### [{site['name']}](site_details?id={site['id']})")
                st.markdown(f"**Location:** {site['location']}, {site['state']}")
                st.markdown(f"**Type:** {site['heritage_type']}")
                st.markdown(f"**Risk Level:** {site['risk_level']}")

                # UNESCO badge
                if site['unesco_status']:
                    st.markdown("![UNESCO](https://via.placeholder.com/100x30?text=UNESCO)")

                # Quick stats
                col3, col4, col5 = st.columns(3)
                with col3:
                    st.metric("Health Index", f"{site['health_index']:.2f}")
                with col4:
                    st.metric("Established", site['established_year'])
                with col5:
                    st.metric("Visitors", "1.2K")

            st.markdown("---")
