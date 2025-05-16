import streamlit as st

def render_filters():
    """Render the filters component for the explore page."""
    filters = {}

    # Heritage Type Filter
    st.markdown("### Heritage Type")
    heritage_type = st.multiselect(
        "Select types",
        ["Cultural", "Natural", "Mixed"],
        label_visibility="collapsed"
    )
    if heritage_type:
        filters['type'] = heritage_type

    # State Filter
    st.markdown("### State")
    state = st.selectbox(
        "Select state",
        ["All", "Delhi", "Maharashtra", "Tamil Nadu", "Karnataka", "Gujarat", "Rajasthan"],
        label_visibility="collapsed"
    )
    if state != "All":
        filters['state'] = state

    # Risk Level Filter
    st.markdown("### Risk Level")
    risk_level = st.multiselect(
        "Select risk levels",
        ["Low", "Medium", "High"],
        label_visibility="collapsed"
    )
    if risk_level:
        filters['risk_level'] = risk_level

    # Year Range Filter
    st.markdown("### Year Established")
    year_range = st.slider(
        "Select year range",
        min_value=0,
        max_value=2024,
        value=(0, 2024),
        label_visibility="collapsed"
    )
    if year_range != (0, 2024):
        filters['year_range'] = year_range

    # UNESCO Status Filter
    st.markdown("### UNESCO Status")
    unesco_status = st.checkbox("UNESCO World Heritage Sites Only")
    if unesco_status:
        filters['unesco_status'] = True

    return filters
