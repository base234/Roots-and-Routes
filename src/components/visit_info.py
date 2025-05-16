import streamlit as st
from utils.database import get_visitor_stats

def render_visit_info(site):
    """Render the visit information section."""
    st.markdown("### Visit Information")

    # Basic information
    st.markdown(f"""
        **Location:** {site['location']}, {site['state']}
        **Coordinates:** {site['latitude']}, {site['longitude']}
        **Established:** {site['established_year']}
    """)

    # Visitor statistics
    visitor_stats = get_visitor_stats(site['id'])
    if visitor_stats:
        st.markdown("### Visitor Statistics")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Average Daily Visitors",
                f"{sum(stat['visitor_count'] for stat in visitor_stats) / len(visitor_stats):.0f}"
            )

        with col2:
            st.metric(
                "Total Revenue",
                f"₹{sum(stat['revenue'] for stat in visitor_stats):,.0f}"
            )

    # Best time to visit
    st.markdown("### Best Time to Visit")
    st.markdown("""
        - **Peak Season:** October to March
        - **Off Season:** April to September
        - **Best Time:** Early morning or late afternoon
    """)

    # Getting there
    st.markdown("### Getting There")
    st.markdown("""
        - **By Air:** Nearest airport information
        - **By Train:** Nearest railway station
        - **By Road:** Road connectivity details
    """)

    # Facilities
    st.markdown("### Facilities")
    st.markdown("""
        - Parking
        - Restrooms
        - Guided Tours
        - Information Center
        - Gift Shop
    """)
