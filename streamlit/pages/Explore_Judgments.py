"""This script displays the judgments page."""

# pylint: disable=invalid-name

from components import dashboard_title  # pylint: disable=import-error
from data_source import get_db_connection, create_client, display_judgment_search  # pylint: disable=import-error
from dashboard_functions import adjust_sidebar_width





def main():
    """This function runs the main block of the webpage."""
    adjust_sidebar_width()
    dashboard_title()
    conn = get_db_connection()
    s_three_client = create_client()
    display_judgment_search(conn, s_three_client)

if __name__ == "__main__":
    main()
