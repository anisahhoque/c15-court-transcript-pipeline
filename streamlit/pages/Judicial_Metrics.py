"""This script displays the page for the Analytics Board page on streamlit."""

# pylint: disable=invalid-name
from dotenv import load_dotenv
from data_source import get_db_connection  # pylint: disable=import-error
from dashboard_functions import cases_by_court, cases_by_judgment_type, adjust_sidebar_width # pylint: disable=import-error
from extra_functions import display_judgments_by_judge, display_number_of_judgments_by_chamber
from components import dashboard_title  # pylint: disable=import-error


def main():
    """Main function to run the analytics page."""
    adjust_sidebar_width()
    load_dotenv()
    conn = get_db_connection()
    dashboard_title()
    display_judgments_by_judge(conn)
    display_number_of_judgments_by_chamber(conn)


if __name__ == "__main__":
    main()
