import streamlit as st
from unsplash.api import Api
from unsplash.auth import Auth
from src.utils.config import UNSPLASH_ACCESS_KEY, UNSPLASH_SECRET_KEY, UNSPLASH_REDIRECT_URI

# Initialize Unsplash API
auth = Auth(
    client_id=UNSPLASH_ACCESS_KEY,
    client_secret=UNSPLASH_SECRET_KEY,
    redirect_uri=UNSPLASH_REDIRECT_URI
)
api = Api(auth)

def fetch_unsplash_images(query, count=9):
    """Fetch images from Unsplash API based on a query."""
    try:
        photos = api.search_photos(query, per_page=count)
        return [photo.urls.regular for photo in photos]
    except Exception as e:
        st.error(f"Failed to fetch images from Unsplash: {e}")
        return []

def render_image_gallery(site_name, count=5):
    """Render a gallery of images for a heritage site."""
    try:
        # Search for images related to the site
        photos = api.search_photos(site_name, per_page=count)

        if photos:
            # Create columns for the gallery
            cols = st.columns(count)

            # Display images in columns
            for idx, photo in enumerate(photos):
                with cols[idx]:
                    st.image(photo.urls.regular, use_container_width=True)
                    st.caption(f"Photo by {photo.user.name} on Unsplash")
        else:
            st.info("No images found for this site.")

    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        return None
