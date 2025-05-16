import streamlit as st
from unsplash.api import Api
from unsplash.auth import Auth
from src.utils.config import UNSPLASH_ACCESS_KEY

# Initialize Unsplash API
auth = Auth(UNSPLASH_ACCESS_KEY)
api = Api(auth)

def fetch_unsplash_images(query, count=9):
    """Fetch images from Unsplash API based on a query."""
    try:
        photos = api.search_photos(query, per_page=count)
        return [photo.urls.regular for photo in photos]
    except Exception as e:
        st.error(f"Failed to fetch images from Unsplash: {e}")
        return []

def render_image_gallery(image_urls=None, query=None, count=9):
    """Render a grid of images using Streamlit. If image_urls is not provided, fetch images from Unsplash."""
    if image_urls is None:
        if query is None:
            st.error("Please provide either image_urls or a query for Unsplash.")
            return
        image_urls = fetch_unsplash_images(query, count)

    if not image_urls:
        st.info("No images available.")
        return

    # Display images in a 3-column grid
    cols = st.columns(3)
    for idx, url in enumerate(image_urls):
        with cols[idx % 3]:
            st.image(url, use_column_width=True)
