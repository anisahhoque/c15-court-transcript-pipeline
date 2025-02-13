"""This script will have the necessary components to run streamlit."""
import streamlit as st


def dashboard_title():
    """Returns the name of the selected page ('Home', 'Judgment Search', or 'Analytics')."""
    st.title("Judgment Reader")
    page = st.sidebar.radio(
        'Select a page', ['Home', 'Judgment Search', 'Analytics'])
    st.markdown(
        f"""
        <h2 style="text-align: center;">{page} Page</h2>
        """,
        unsafe_allow_html=True
    )
    return page
