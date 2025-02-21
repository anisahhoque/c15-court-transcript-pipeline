"""This script displays the page for the Courts page on streamlit."""


from dotenv import load_dotenv
from data_source import get_db_connection  # pylint: disable=import-error
from dashboard_functions import adjust_sidebar_width
from extra_functions import compare_chambers, display_judgments_for_court  # pylint: disable=import-error

from components import dashboard_title  # pylint: disable=import-error

def main():
    """Main function to run the analytics page."""
    adjust_sidebar_width()
    load_dotenv()
    conn = get_db_connection()
    dashboard_title()
    display_judgments_for_court(conn)
    compare_chambers(conn)



if __name__ == "__main__":
    main()
