"""The main page of the dashboard."""
from os import environ as ENV
from dotenv import load_dotenv
import streamlit as st

from data_source import get_db_connection
from components import dashboard_title


if __name__ == "__main__":
    load_dotenv()

    dashboard_title()

    