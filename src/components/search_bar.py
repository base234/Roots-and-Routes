import streamlit as st
from src.utils.config import DISCOVERY_CONFIG
from src.utils.database import get_heritage_sites

def render_search_bar():
    st.markdown('<p class="search-subtitle">Search and plan your next visit</p>', unsafe_allow_html=True)

    # Search input
    search_query = st.text_input(
        "Search",
        placeholder="Search for heritage sites, locations, or cultural events...",
        key="main_search",
        label_visibility="collapsed"
    )

    # Advanced filters
    use_advanced_filters = st.checkbox("Use Advanced Filters", value=False)

    if use_advanced_filters:
        col1, col2, col3, col4 = st.columns(4)

        with st.container():
          with col1:
                state = st.selectbox(
                    "State",
                ["None", "Maharashtra", "Karnataka", "Tamil Nadu", "Rajasthan", "Uttar Pradesh",
                 "Madhya Pradesh", "Odisha", "Delhi", "Gujarat", "Telangana", "West Bengal", "Assam"],
                index=0
            )

          with col2:
            heritage_type = st.selectbox(
                "Heritage Type",
                ["None", "Monument", "Temple", "Ruins", "Cave", "Fort", "Palace", "Bridge",
                 "Road", "Observatory", "Forest", "Park"],
                index=0
            )

          with col3:
            conservation_status = st.selectbox(
                "Conservation Status",
                ["None", "Low", "Medium", "High"],
                index=0
            )

          with col4:
            risk_level = st.selectbox(
                "Risk Level",
                ["None", "Low", "Medium", "High"],
                index=0
            )

        col1, col2 = st.columns(2)

        with st.container():
          with col1:
            st.markdown("Year Range")

        col1, col2, col3, col4 = st.columns(4)
        with st.container():
          with col1:
            from_year = st.number_input("From", min_value=200, max_value=2025, value=200, step=1, label_visibility="collapsed")
          with col2:
              to_year = st.number_input("To", min_value=1000, max_value=2025, value=2025, step=1, label_visibility="collapsed")

        # UNESCO checkboxes in a new line
        st.markdown('<div class="unesco-checkboxes">', unsafe_allow_html=True)
        unesco = st.checkbox("UNESCO", value=False)
        non_unesco = st.checkbox("Non-UNESCO", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # Search button and results
    if st.button("Search", key="search_button"):
        # Prepare filters dictionary
        filters = {}

        # Add search query if provided
        if search_query:
            filters['search_query'] = search_query
            st.success(f"Searching for: {search_query}")

        # Add advanced filters if enabled and selected
        if use_advanced_filters:
            if state != "None":
                filters['state'] = state
            if heritage_type != "None":
                filters['type'] = [heritage_type]
            if conservation_status != "None":
                filters['conservation_status'] = [conservation_status]
            if risk_level != "None":
                filters['risk_level'] = [risk_level]

            # Handle UNESCO status filters
            if unesco or non_unesco:
                if unesco and not non_unesco:
                    filters['unesco_status'] = True
                elif non_unesco and not unesco:
                    filters['unesco_status'] = False
                # If both are checked, don't filter by UNESCO status

            # Add year range filter
            if from_year != 1000 or to_year != 2024:
                filters['year_range'] = [from_year, to_year]

        # Get search results
        results = get_heritage_sites(filters)

        # Display results
        if results:
            st.markdown('<div class="search-results">', unsafe_allow_html=True)
            for site in results:
                st.markdown(f"""
                    <div class="result-card">
                        <h3 class="result-title">{site['name']}</h3>
                        <p class="result-details"><strong>Location:</strong> {site['location']}</p>
                        <p class="result-details"><strong>Type:</strong> {site['heritage_type']}</p>
                        <p class="result-details"><strong>Status:</strong> {site['risk_level']}</p>
                        <p class="result-details"><strong>UNESCO:</strong> {"Yes" if site['unesco_status'] else "No"}</p>
                        <p class="result-details">{site['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No heritage sites found matching your search criteria.")

    return search_query
