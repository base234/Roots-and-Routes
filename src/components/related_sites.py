import streamlit as st

def render_related_sites(sites):
    """Render the related sites section."""
    if not sites:
        return

    for site in sites:
        with st.container():
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(
                    "https://via.placeholder.com/100",
                    width=100
                )

            with col2:
                st.markdown(f"**{site['name']}**")
                st.markdown(f"*{site['location']}, {site['state']}*")
                st.markdown(f"Type: {site['heritage_type']}")
                st.button("View", key=f"related_{site['id']}")
