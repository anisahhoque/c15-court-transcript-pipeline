import streamlit as st
from dotenv import load_dotenv
from data_source import get_db_connection
from dashboard_functions import cases_by_court, cases_by_judgment_type

from components import dashboard_title

def main():
    load_dotenv()
    conn = get_db_connection()
    dashboard_title()
    cases_by_court(conn)
    cases_by_judgment_type(conn)
    


if __name__ == "__main__":
    main()
