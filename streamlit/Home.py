"""The main page of the dashboard."""

from dotenv import load_dotenv
import streamlit as st
from components import dashboard_title, homepage_text
from data_source import (get_most_recent_judgments,
                         get_db_connection,
                         display_as_table, get_most_recent_judgment, display_judgment,
                         get_random_judgment_with_summary_and_date)

from dashboard_functions import cases_by_court, cases_by_judgment_type, apply_custom_styles

def main():
    """Runs the complete scripts."""

    import streamlit as st

    apply_custom_styles()
    load_dotenv()
    dashboard_title()
    homepage_text()
    conn = get_db_connection()
    results = get_most_recent_judgments(conn)
    display_as_table(results)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most Recent Case")
        most_recent_judg = get_most_recent_judgment(conn)
        display_judgment(most_recent_judg)

    with col2:
        st.subheader("Case of the Day")
        random_judg = get_random_judgment_with_summary_and_date(conn)
        display_judgment(random_judg)
    

    cases_by_court(conn)
    
    cases_by_judgment_type(conn)
        




if __name__ == "__main__":
    main()
