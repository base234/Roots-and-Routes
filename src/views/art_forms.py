import streamlit as st
from src.utils.database import get_all_art_forms
from src.utils.config import UNSPLASH_ACCESS_KEY
import requests

def get_art_form_image(art_form_name):
    """Fetch a relevant image for the art form from Unsplash."""
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{art_form_name} art form India",
                "per_page": 1
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            },
            timeout=5
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

def render_art_forms_page():
    """Render the art forms page with all available art forms."""
    st.markdown("## Art Forms")
    st.markdown("Discover traditional and contemporary art forms from across India")

    # Get all art forms
    art_forms = get_all_art_forms()

    if not art_forms:
        st.info("No art forms available at the moment.")
        return

    # Get unique states and categories for filters
    states = sorted(list(set(art_form['origin_state'] for art_form in art_forms)))
    states.insert(0, "All States")  # Add "All States" as the first option

    categories = sorted(list(set(art_form['category'] for art_form in art_forms)))
    categories.insert(0, "All Categories")  # Add "All Categories" as the first option

    # Create two columns for filters
    col1, col2 = st.columns(2)

    # Add state filter in first column
    with col1:
        selected_state = st.selectbox(
            "Filter by State",
            states,
            index=0
        )

    # Add category filter in second column
    with col2:
        selected_category = st.selectbox(
            "Filter by Category",
            categories,
            index=0
        )

    # Filter art forms by selected state
    if selected_state != "All States":
        art_forms = [art_form for art_form in art_forms if art_form['origin_state'] == selected_state]

    # Filter art forms by selected category
    if selected_category != "All Categories":
        art_forms = [art_form for art_form in art_forms if art_form['category'] == selected_category]

    # Show count of art forms found
    if selected_state == "All States":
        st.markdown(f"Found {len(art_forms)} art forms across India")
    else:
        st.markdown(f"Found {len(art_forms)} art forms in {selected_state}")

    # Display art forms in rows of 4
    for i in range(0, len(art_forms), 4):
        # Create a row of 4 columns
        cols = st.columns(4)

        # Fill each column with an art form
        for j in range(4):
            if i + j < len(art_forms):
                art_form = art_forms[i + j]
                with cols[j]:
                    # Get art form image
                    image_url = get_art_form_image(art_form['name'])
                    if not image_url:
                        image_url = "https://via.placeholder.com/400x300?text=No+Image+Available"

                    # Display art form image
                    st.image(image_url, use_container_width=True)

                    # Display art form information
                    st.markdown(f"**{art_form['name']}**")

                    # Display category tag
                    st.markdown(
                        f'<div style="background-color: #4CAF50; color: white; padding: 2px 8px; border-radius: 4px; display: inline-block; margin: 4px 0;">'
                        f'🎨 {art_form["category"]}'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    # Display origin state
                    st.markdown(f"*Origin: {art_form['origin_state']}*")

                    # Display practitioners count if available
                    if art_form.get('practitioners_count'):
                        st.markdown(f"*Practitioners: {art_form['practitioners_count']}*")

                    # Add view details button
                    if st.button("View Details", key=f"view_{art_form['name']}"):
                        st.session_state['selected_art_form'] = art_form['name']
                        st.session_state['current_view'] = 'art_form_details'
                        st.rerun()

                    st.markdown("---")  # Add separator between art forms
