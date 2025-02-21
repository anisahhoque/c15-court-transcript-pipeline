"""This script displays the page for the Courts page on streamlit."""


from dotenv import load_dotenv
from data_source import get_db_connection  # pylint: disable=import-error
from dashboard_functions import display_judgments_for_court, adjust_sidebar_width  # pylint: disable=import-error
import streamlit as st
from components import dashboard_title  # pylint: disable=import-error

def main():
    """Main function to run the analytics page."""
    adjust_sidebar_width()
    with open("style.css") as css:
            st.html(f'<style>{css.read()}</style>')
    load_dotenv()
    conn = get_db_connection()
    dashboard_title()
    display_judgments_for_court(conn)


if __name__ == "__main__":
    main()
