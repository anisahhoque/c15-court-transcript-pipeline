"""Functions that handle communication with the database."""

from os import environ as ENV

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import streamlit as st
import pandas as pd
from dotenv import load_dotenv


@st.cache_resource
def get_db_connection() -> connection:
    """Returns a live connection to the local PostgreSQL database."""
    config = {
        "dbname": ENV.get("DB_NAME"),
        "user": ENV.get("DB_USER"),
        "password": ENV.get("DB_PASSWORD"),
        "host": ENV.get("DB_HOST"),
        "port": ENV.get("DB_PORT")
    }

    return connect(**config)

@st.cache_resource
def get_latest_cases(connection):

    query = """SELECT * FR"""
    