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
       The Court Transcript Pipeline is an automated system designed to enhance
       the accessibility and analysis of real courtroom documents.
       Every day, the National Archives releases court transcripts, but they are difficult to search, analyze,
       and consume for the average person. This project processes these transcripts, extracts key details, and summarizes important information using AI.
       With a powerful search dashboard, users can explore court judgments, track judicial trends, and uncover
       insights about courtroom proceedings. Whether you're a journalist,
       researcher, or citizen, this tool makes legal data more transparent and discoverable.</p>
        """,
        unsafe_allow_html=True
    )
