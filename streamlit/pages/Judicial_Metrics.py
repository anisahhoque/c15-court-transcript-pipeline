"""This script displays the page for the Analytics Board page on streamlit."""

# pylint: disable=invalid-name
from dotenv import load_dotenv
from data_source import get_db_connection  # pylint: disable=import-error
from dashboard_functions import cases_by_court, cases_by_judgment_type, display_judgments_by_judge, display_number_of_judgments_by_chamber, apply_custom_styles  # pylint: disable=import-error

from components import dashboard_title  # pylint: disable=import-error


def main():
    """Main function to run the analytics page."""
    apply_custom_styles()
    load_dotenv()
    conn = get_db_connection()
    dashboard_title()
    display_judgments_by_judge(conn)
    display_number_of_judgments_by_chamber(conn)


if __name__ == "__main__":
    main()
