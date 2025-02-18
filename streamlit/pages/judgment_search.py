import streamlit as st

from components import dashboard_title
from data_source import fetch_judgments, get_db_connection, display_judgment_search



def main():
    dashboard_title()
    conn = get_db_connection()
    display_judgment_search(conn)

if __name__ == "__main__":
    main()
