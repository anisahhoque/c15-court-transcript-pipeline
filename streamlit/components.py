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
        <p style="text-align: justify">
       Welcome to the Court Transcript Pipeline – an AI-powered system that transforms courtroom documents into searchable, insightful, and easily accessible legal data.</p>
        """,
        unsafe_allow_html=True
    )
