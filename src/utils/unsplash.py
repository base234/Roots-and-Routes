import streamlit as st
import requests
from src.utils.config import UNSPLASH_ACCESS_KEY

def get_site_images(site_name, count=5):
    """Fetch multiple relevant images for the heritage site from Unsplash."""
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{site_name} india",
                "per_page": count
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
        )
        data = response.json()
        if data['results']:
            return [result['urls']['regular'] for result in data['results']]
    except Exception as e:
        st.warning(f"Could not fetch images: {str(e)}")
    return None
