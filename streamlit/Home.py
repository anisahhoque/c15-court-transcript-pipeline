"""The main page of the dashboard."""

from dotenv import load_dotenv
import streamlit as st
from components import dashboard_title, homepage_text
from data_source import (get_most_recent_judgments,
                         get_db_connection,
                         display_as_table, get_most_recent_judgment, display_judgment,
                         get_random_judgment_with_summary_and_date,
                         cases_over_time)

from dashboard_functions import cases_by_court, cases_by_judgment_type, adjust_sidebar_width


def main():
    """Runs the complete scripts."""
    st.set_page_config(layout="wide")
    #css
    adjust_sidebar_width()
    with open("style.css") as css:
        st.html(f'<style>{css.read()}</style>')
    load_dotenv()
    dashboard_title()
    homepage_text()
    conn = get_db_connection()
    col1, col2 = st.columns(2)
    with col1:
        st.html("<h2>Most Recent Judgment")
        most_recent_judgement = get_most_recent_judgment(conn)
        display_judgment(most_recent_judgement)

    with col2:
        st.html("<h2>🌟Judgment of the Day")
        random_judgment = get_random_judgment_with_summary_and_date(conn)
        display_judgment(random_judgment)


    col3,col4 = st.columns(2)
    with col3:
        cases_over_time(conn)
    with col4:
        cases_by_judgment_type(conn)
    cases_by_court(conn)

    results = get_most_recent_judgments(conn)
    display_as_table(results)

if __name__ == "__main__":
    main()
