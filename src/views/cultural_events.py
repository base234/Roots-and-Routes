import streamlit as st
from src.utils.database import get_all_cultural_events
from src.utils.config import UNSPLASH_ACCESS_KEY
import requests

def get_event_image(event_name):
    """Fetch a relevant image for the cultural event from Unsplash."""
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{event_name} cultural event india",
                "per_page": 1
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            },
            timeout=5  # Add timeout
        )

        # Check if response is successful
        if response.status_code != 200:
            return "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop"

        data = response.json()
        if data and 'results' in data and data['results']:
            return data['results'][0]['urls']['regular']

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
    except ValueError as e:
        print(f"JSON parsing error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    # Return a default image if anything fails
    return "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=1000&auto=format&fit=crop"

def render_cultural_events_page():
    """Render the cultural events page with all available events."""
    # Add custom CSS for fixed image sizes
    st.markdown("""
        <style>
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

    st.markdown("## Cultural Events")

    # Get all cultural events
    events = get_all_cultural_events()

    if not events:
        st.info("No cultural events available at the moment.")
        return

    # Get unique states for the filter
    states = sorted(list(set(event['location'] for event in events)))
    states.insert(0, "All States")  # Add "All States" as the first option

    # Create two columns for filters
    col1, col2 = st.columns(2)

    # Add state filter in first column
    with col1:
        selected_state = st.selectbox(
            "Filter by State",
            states,
            index=0
        )

    # Add event type filter in second column
    with col2:
        event_types = sorted(list(set(event['event_type'] for event in events)))
        event_types.insert(0, "All Types")
        selected_type = st.selectbox(
            "Event Type",
            event_types,
            index=0
        )

    # Filter events by selected state
    if selected_state != "All States":
        events = [event for event in events if event['location'] == selected_state]

    # Filter events by selected type
    if selected_type != "All Types":
        events = [event for event in events if event['event_type'] == selected_type]

    # Show count of events found
    if selected_state == "All States":
        st.markdown(f"Found {len(events)} cultural events across India")
    else:
        st.markdown(f"Found {len(events)} cultural events in {selected_state}")

    # Display events in rows of 4
    for i in range(0, len(events), 4):
        # Create a row of 4 columns
        cols = st.columns(4)

        # Fill each column with an event
        for j in range(4):
            if i + j < len(events):
                event = events[i + j]
                with cols[j]:
                    # Get event image
                    image_url = get_event_image(event['name'])
                    if not image_url:
                        image_url = "https://via.placeholder.com/400x200?text=No+Image+Available"

                    # Display event image
                    st.image(image_url, use_container_width=True)

                    # Display event information
                    st.markdown(f"**{event['name']}**")
                    st.markdown(f"*{event['location']}*")

                    # Display event type tag
                    st.markdown(
                        '<div style="color: #1E88E5; display: inline-block;">'
                        f'🎭 {event["event_type"]}'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(" ")
                    st.markdown(" ")

                    # Add view details button
                    if st.button("View Details", key=f"view_{event['name']}"):
                        st.session_state['selected_event'] = event['name']
                        st.session_state['current_view'] = 'event_details'
                        st.rerun()
        st.markdown(" ")
