"""This script displays the judgments page."""

# pylint: disable=invalid-name

from components import dashboard_title  # pylint: disable=import-error
from data_source import get_db_connection, display_judgment_search  # pylint: disable=import-error
from dashboard_functions import apply_custom_styles



def main():
    """This function runs the main block of the webpage."""
    apply_custom_styles()
    
    dashboard_title()
    conn = get_db_connection()
    display_judgment_search(conn)

if __name__ == "__main__":
    main()
