"""This script will have the necessary components to run streamlit."""
import streamlit as st


def dashboard_title() -> None:
    """Returns the name of the selected page ('Home', 'Judgment Search', or 'Analytics')."""
    st.markdown(
        """
    <h1 style="text-align: center;">Judgment Reader</h1>
    """,
        unsafe_allow_html=True
    )


def homepage_text() -> None:
    """Use st.markdown to center the subheader/"""
    st.markdown(
        """
        <p style="text-align: center">
       Welcome to the Court Transcript Pipeline.</p>
        """,
        unsafe_allow_html=True
    )
