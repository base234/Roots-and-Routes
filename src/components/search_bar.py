import streamlit as st
from src.utils.config import DISCOVERY_CONFIG, UNSPLASH_ACCESS_KEY
from src.utils.database import get_heritage_sites, get_art_forms, get_cultural_events
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
                num_cols = 3
                num_rows = (len(sites) + num_cols - 1) // num_cols

                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col in range(num_cols):
                        idx = row * num_cols + col
                        if idx < len(sites):
                            site = sites[idx]
                            with cols[col]:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                image_url = get_site_image(f"{site['name']} {site['heritage_type']} {site['location']}")
                                if image_url:
                                    st.image(image_url, use_container_width=True)
                                else:
                                    st.image("https://via.placeholder.com/400x200?text=No+Image", use_container_width=True)

                                st.markdown('<div class="result-content">', unsafe_allow_html=True)
                                st.markdown(f"""
                                    <h3 class="result-title">{site['name']}</h3>
                                    <p class="result-details"><strong>Location:</strong> {site['location']}</p>
                                    <p class="result-details"><strong>Type:</strong> {site['heritage_type']}</p>
                                    <p class="result-details"><strong>Status:</strong> {site['risk_level']}</p>
                                    <p class="result-details"><strong>UNESCO:</strong> {"Yes" if site['unesco_status'] else "No"}</p>
                                    <p class="result-details">{site['description']}</p>
                                    {f"<p class='result-details'><strong>Historical Significance:</strong> {site.get('historical_significance', '')}</p>" if 'historical_significance' in site else ''}
                                    {f"<p class='result-details'><strong>Conservation Efforts:</strong> {site.get('conservation_efforts', '')}</p>" if 'conservation_efforts' in site else ''}
                                """, unsafe_allow_html=True)
                                st.markdown('</div></div>', unsafe_allow_html=True)

            if 'art_forms' in results and results['art_forms']:
                arts = results['art_forms']
                st.markdown(f"### Art Forms ({len(arts)})")
                num_cols = 3
                num_rows = (len(arts) + num_cols - 1) // num_cols

                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col in range(num_cols):
                        idx = row * num_cols + col
                        if idx < len(arts):
                            art = arts[idx]
                            with cols[col]:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                image_url = get_site_image(f"{art['name']} {art['category']} {art['origin_state']}")
                                if image_url:
                                    st.image(image_url, use_container_width=True)
                                else:
                                    st.image("https://via.placeholder.com/400x200?text=No+Image", use_container_width=True)

                                st.markdown('<div class="result-content">', unsafe_allow_html=True)
                                st.markdown(f"""
                                    <h3 class="result-title">{art['name']}</h3>
                                    <p class="result-details"><strong>Category:</strong> {art['category']}</p>
                                    <p class="result-details"><strong>Origin State:</strong> {art['origin_state']}</p>
                                    <p class="result-details"><strong>Risk Level:</strong> {art['risk_level']}</p>
                                    <p class="result-details"><strong>Practitioners:</strong> {art['practitioners_count']}</p>
                                    <p class="result-details">{art['description']}</p>
                                    {f"<p class='result-details'><strong>Techniques:</strong> {art.get('techniques', '')}</p>" if 'techniques' in art else ''}
                                    {f"<p class='result-details'><strong>Cultural Significance:</strong> {art.get('cultural_significance', '')}</p>" if 'cultural_significance' in art else ''}
                                """, unsafe_allow_html=True)
                                st.markdown('</div></div>', unsafe_allow_html=True)

            if 'cultural_events' in results and results['cultural_events']:
                events = results['cultural_events']
                st.markdown(f"### Cultural Events ({len(events)})")
                num_cols = 3
                num_rows = (len(events) + num_cols - 1) // num_cols

                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col in range(num_cols):
                        idx = row * num_cols + col
                        if idx < len(events):
                            event = events[idx]
                            with cols[col]:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                image_url = get_site_image(f"{event['name']} {event['event_type']} {event['location']}")
                                if image_url:
                                    st.image(image_url, use_container_width=True)
                                else:
                                    st.image("https://via.placeholder.com/400x200?text=No+Image", use_container_width=True)

                                st.markdown('<div class="result-content">', unsafe_allow_html=True)
                                st.markdown(f"""
                                    <h3 class="result-title">{event['name']}</h3>
                                    <p class="result-details"><strong>Type:</strong> {event['event_type']}</p>
                                    <p class="result-details"><strong>Location:</strong> {event['location']}</p>
                                    <p class="result-details"><strong>Organizer:</strong> {event['organizer']}</p>
                                    <p class="result-details"><strong>Date:</strong> {event['start_date']} to {event['end_date']}</p>
                                    <p class="result-details">{event['description']}</p>
                                    {f"<p class='result-details'><strong>Activities:</strong> {event.get('activities', '')}</p>" if 'activities' in event else ''}
                                    {f"<p class='result-details'><strong>Highlights:</strong> {event.get('highlights', '')}</p>" if 'highlights' in event else ''}
                                """, unsafe_allow_html=True)
                                st.markdown('</div></div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No results found matching your search criteria.")

    return search_query
