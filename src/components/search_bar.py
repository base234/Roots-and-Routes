import streamlit as st
from src.utils.config import DISCOVERY_CONFIG, UNSPLASH_ACCESS_KEY
from src.utils.database import get_heritage_sites, get_all_heritage_sites, get_art_forms, get_all_art_forms, get_cultural_events, get_all_cultural_events
import requests

def get_site_image(query):
    """Fetch a relevant image from Unsplash."""
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{query}",
                "per_page": 1
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
        )
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    except Exception as e:
        st.warning(f"Could not fetch image: {str(e)}")
    return None

def display_results_grid(items, item_type):
    """Display items in a 4-column grid."""
    if not items:
        st.info(f"No {item_type} available.")
        return

    num_cols = 4
    num_rows = (len(items) + num_cols - 1) // num_cols

    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < len(items):
                item = items[idx]
                with cols[col]:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)

                    # Get image based on item type
                    if item_type == "Heritage Sites":
                        image_url = get_site_image(f"{item['name']} {item['heritage_type']} {item['location']}")
                        content = f"""
                            <h3 class="result-title">{item['name']}</h3>
                            <p class="result-details"><strong>Location:</strong> {item['location']}</p>
                            <p class="result-details"><strong>Type:</strong> {item['heritage_type']}</p>
                            <p class="result-details"><strong>Status:</strong> {item['risk_level']}</p>
                            <p class="result-details"><strong>UNESCO:</strong> {"Yes" if item['unesco_status'] else "No"}</p>
                            <p class="result-details">{item['description']}</p>
                            {f"<p class='result-details'><strong>Historical Significance:</strong> {item.get('historical_significance', '')}</p>" if 'historical_significance' in item else ''}
                            {f"<p class='result-details'><strong>Conservation Efforts:</strong> {item.get('conservation_efforts', '')}</p>" if 'conservation_efforts' in item else ''}
                        """
                    elif item_type == "Art Forms":
                        image_url = get_site_image(f"{item['name']} {item['category']} {item['origin_state']}")
                        content = f"""
                            <h3 class="result-title">{item['name']}</h3>
                            <p class="result-details"><strong>Category:</strong> {item['category']}</p>
                            <p class="result-details"><strong>Origin State:</strong> {item['origin_state']}</p>
                            <p class="result-details"><strong>Risk Level:</strong> {item['risk_level']}</p>
                            <p class="result-details"><strong>Practitioners:</strong> {item['practitioners_count']}</p>
                            <p class="result-details">{item['description']}</p>
                            {f"<p class='result-details'><strong>Techniques:</strong> {item.get('techniques', '')}</p>" if 'techniques' in item else ''}
                            {f"<p class='result-details'><strong>Cultural Significance:</strong> {item.get('cultural_significance', '')}</p>" if 'cultural_significance' in item else ''}
                        """
                    else:  # Cultural Events
                        image_url = get_site_image(f"{item['name']} {item['event_type']} {item['location']}")
                        content = f"""
                            <h3 class="result-title">{item['name']}</h3>
                            <p class="result-details"><strong>Type:</strong> {item['event_type']}</p>
                            <p class="result-details"><strong>Location:</strong> {item['location']}</p>
                            <p class="result-details"><strong>Organizer:</strong> {item['organizer']}</p>
                            <p class="result-details"><strong>Date:</strong> {item['start_date']} to {item['end_date']}</p>
                            <p class="result-details">{item['description']}</p>
                            {f"<p class='result-details'><strong>Activities:</strong> {item.get('activities', '')}</p>" if 'activities' in item else ''}
                            {f"<p class='result-details'><strong>Highlights:</strong> {item.get('highlights', '')}</p>" if 'highlights' in item else ''}
                        """

                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/400x200?text=No+Image", use_container_width=True)

                    st.markdown('<div class="result-content">', unsafe_allow_html=True)
                    st.markdown(content, unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

def render_search_bar():
    # Add custom CSS for fixed image sizes and consistent card appearance
    st.markdown("""
        <style>
        .result-card {
            border-radius: 8px;
            padding: 0;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .result-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        .result-content {
            padding: 15px;
        }
        .result-title {
            margin-top: 0;
            font-size: 1.2em;
            font-weight: bold;
        }
        .result-details {
            font-size: 0.9em;
            margin: 5px 0;
        }
        .expanded-details {
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        div[data-testid="stImage"] {
            width: 100%;
            height: 200px;
            object-fit: cover;
            margin: 0;
        }
        div[data-testid="stImage"] img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Search", "Heritage Sites", "Cultural Events", "Art Forms"])

    with tab1:
        # Search type selection
        search_type = st.radio(
            "Search and plan your next visit",
            ["All", "Heritage Sites", "Art Forms", "Cultural Events"],
            horizontal=True,
            key="search_type"
        )

        # Search input
        search_query = st.text_input(
            "Search",
            placeholder="Search for heritage sites, art forms, or cultural events...",
            key="main_search",
            label_visibility="collapsed"
        )

        # Initialize use_advanced_filters
        use_advanced_filters = False

        # Advanced filters - only show for specific search types
        if search_type in ["Heritage Sites", "Art Forms", "Cultural Events"]:
            use_advanced_filters = st.checkbox("Use Advanced Filters", value=False)

            if use_advanced_filters:
                if search_type == "Heritage Sites":
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

                elif search_type == "Art Forms":
                    col1, col2, col3 = st.columns(3)

                    with st.container():
                        with col1:
                            art_category = st.selectbox(
                                "Category",
                                ["None", "Dance", "Painting", "Textile", "Theatre", "Ritual"],
                                index=0
                            )

                        with col2:
                            origin_state = st.selectbox(
                                "Origin State",
                                ["None", "Kerala", "Uttar Pradesh", "Tamil Nadu", "Andhra Pradesh", "Odisha",
                                 "Manipur", "Assam", "Bihar", "West Bengal", "Maharashtra", "Punjab",
                                 "Madhya Pradesh", "Gujarat", "Karnataka", "Rajasthan"],
                                index=0
                            )

                        with col3:
                            risk_level = st.selectbox(
                                "Risk Level",
                                ["None", "Low", "Medium", "High"],
                                index=0
                            )

                elif search_type == "Cultural Events":
                    col1, col2, col3 = st.columns(3)

                    with st.container():
                        with col1:
                            event_type = st.selectbox(
                                "Event Type",
                                ["None", "Dance Festival", "Music Festival", "Cultural Festival", "Eco Festival", "Wildlife Festival"],
                                index=0
                            )

                        with col2:
                            location = st.selectbox(
                                "Location",
                                ["None", "Khajuraho", "Konark", "Aurangabad", "Mahabalipuram", "Pattadakal",
                                 "Delhi", "Mumbai", "Hampi", "Agra", "Sanchi", "Fatehpur Sikri", "Thanjavur",
                                 "Champaner", "Patan", "Mysore", "Madurai", "Guwahati", "Sundarbans", "Kaziranga"],
                                index=0
                            )

                        with col3:
                            organizer = st.selectbox(
                                "Organizer",
                                ["None", "MP Tourism", "Odisha Tourism", "Maharashtra Tourism", "Tamil Nadu Tourism",
                                 "Karnataka Tourism", "Delhi Tourism", "UP Tourism", "Gujarat Tourism", "Assam Tourism",
                                 "West Bengal Tourism"],
                                index=0
                            )

        # Search button
        search_clicked = st.button("Search", key="search_button")

        if search_clicked:
            # Check if search query is empty
            if not search_query and not use_advanced_filters:
                st.info("Please enter a search term or use advanced filters to search.")
                return

            # Prepare filters dictionary
            filters = {}

            # Add search query if provided
            if search_query:
                filters['search_query'] = search_query
                st.success(f"Searching for: {search_query}")

            # Add advanced filters if enabled and selected
            if search_type in ["Heritage Sites", "Art Forms", "Cultural Events"] and use_advanced_filters:
                if search_type == "Heritage Sites":
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

                    # Add year range filter
                    if from_year != 1000 or to_year != 2024:
                        filters['year_range'] = [from_year, to_year]

                elif search_type == "Art Forms":
                    if art_category != "None":
                        filters['category'] = art_category
                    if origin_state != "None":
                        filters['origin_state'] = origin_state
                    if risk_level != "None":
                        filters['risk_level'] = risk_level

                elif search_type == "Cultural Events":
                    if event_type != "None":
                        filters['event_type'] = event_type
                    if location != "None":
                        filters['location'] = location
                    if organizer != "None":
                        filters['organizer'] = organizer

            # Get search results based on search type
            if search_type == "All":
                results = {
                    'heritage_sites': get_heritage_sites(filters),
                    'art_forms': get_art_forms(filters),
                    'cultural_events': get_cultural_events(filters)
                }
            elif search_type == "Heritage Sites":
                results = {'heritage_sites': get_heritage_sites(filters)}
            elif search_type == "Art Forms":
                results = {'art_forms': get_art_forms(filters)}
            elif search_type == "Cultural Events":
                results = {'cultural_events': get_cultural_events(filters)}

            # Display results
            if any(results.values()):
                # Calculate total results
                total_results = sum(len(v) for v in results.values())
                st.markdown(f"### Found {total_results} results")
                st.markdown('<div class="search-results">', unsafe_allow_html=True)

                if 'heritage_sites' in results and results['heritage_sites']:
                    sites = results['heritage_sites']
                    st.markdown(f"### Heritage Sites ({len(sites)})")
                    display_results_grid(sites, "Heritage Sites")

                if 'art_forms' in results and results['art_forms']:
                    arts = results['art_forms']
                    st.markdown(f"### Art Forms ({len(arts)})")
                    display_results_grid(arts, "Art Forms")

                if 'cultural_events' in results and results['cultural_events']:
                    events = results['cultural_events']
                    st.markdown(f"### Cultural Events ({len(events)})")
                    display_results_grid(events, "Cultural Events")

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No results found matching your search criteria.")

    with tab2:
        sites = get_all_heritage_sites()
        st.markdown(f"### Heritage Sites ({len(sites)})")
        display_results_grid(sites, "Heritage Sites")

    with tab3:
        events = get_all_cultural_events()
        st.markdown(f"### Cultural Events ({len(events)})")
        display_results_grid(events, "Cultural Events")

    with tab4:
        arts = get_all_art_forms()
        st.markdown(f"### Art Forms ({len(arts)})")
        display_results_grid(arts, "Art Forms")

    return search_query
