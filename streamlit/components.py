"""This script will have the necessary components to run streamlit."""
import streamlit as st


def dashboard_title() -> None:
    """Returns the name of the selected page ('Home', 'Judgment Search', or 'Analytics')."""
    st.title("Judgment Reader")


def homepage_text() -> None:
    """Use st.markdown to center the subheader/"""
    st.markdown(
        """
        <h2 style="text-align: center;">Home</h2>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p style="text-align: center;">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor 
        in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt 
        in culpa qui officia deserunt mollit anim id est laborum.
        </p>
        """,
        unsafe_allow_html=True
    )
