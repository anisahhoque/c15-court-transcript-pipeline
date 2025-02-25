"""This script will have the necessary components to run streamlit."""
import streamlit as st


def dashboard_title() -> None:
    """Returns the name of the selected page ('Home', 'Judgment Search', or 'Analytics')."""
    st.html(
        """
        <header style="text-align: center; font-size: 60px;">Judgment Reader</header>
        """
    )



def homepage_text() -> None:
    """Use st.markdown to center the subheader/"""
    st.html(
        """
        <p style="text-align: center">
       Welcome to the Court Transcript Pipeline.</p>
        """
    )
