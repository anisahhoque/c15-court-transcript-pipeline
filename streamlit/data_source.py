from os import environ as ENV
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import streamlit as st
from dotenv import load_dotenv
import pandas as pd


@st.cache_resource
def get_db_connection() -> connection:
    """Returns a live connection to PostgreSQL database with RealDictCursor as default."""
    config = {
        "dbname": ENV.get("DB_NAME"),
        "user": ENV.get("DB_USER"),
        "password": ENV.get("DB_PASSWORD"),
        "host": ENV.get("DB_HOST"),
        "port": ENV.get("DB_PORT"),  # Default to '5432' if not set
    }

    # Include RealDictCursor as the cursor_factory in the connection
    return connect(cursor_factory=RealDictCursor, **config)


@st.cache_resource
def get_most_recent_judgments(_conn):
    """Fetches the most recent cases from the database, returning them as a list of dictionaries."""

    query = """SELECT j.neutral_citation AS judgment, jd.judge_name AS judge, c.court_name as court
                FROM judgment j
                JOIN judge jd ON j.neutral_citation = jd.neutral_citation
                JOIN court c ON j.court_id = c.court_id;"""

    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()  # This will return the results as a list of dictionaries


def display_as_table(results: list):
    """Converts a list of dictionaries into a Pandas DataFrame, capitalizes the column titles, and displays it as a table in Streamlit."""
    df = pd.DataFrame(results)

    df.columns = [col.capitalize() for col in df.columns]

    df = df.reset_index(drop=True)
    st.subheader("New Daily Cases")
    st.dataframe(df, hide_index=True, use_container_width=True)

@st.cache_resource
def get_most_recent_judgment(_conn):
    """Returns latest story."""

    query = """SELECT 
    j.neutral_citation, 
    j.court_id, 
    j.hearing_date, 
    j.judgement_date, 
    a.argument_id, 
    a.summary AS argument_summary
    FROM 
    judgment j
    JOIN 
    argument a ON j.neutral_citation = a.neutral_citation
    ORDER BY 
    j.judgement_date DESC
    LIMIT 1;
    """

    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchone()


def display_judgment(judgment_data):
    # Extract data from the dictionary
    neutral_citation = judgment_data.get("neutral_citation")
    argument_summary = judgment_data.get("argument_summary")
    judgment_date = judgment_data.get("judgement_date")

    # If we have a result, display it
    if neutral_citation and argument_summary:
        st.subheader(neutral_citation)  # Displaying neutral_citation as the title
        st.text(judgment_date)
        st.text(argument_summary)   # Displaying the argument summary as text
        
    else:
        st.write("No judgment found.")


def get_random_judgment_with_summary_and_date(_conn):
    try:
        # Using 'with' to ensure cursor is properly closed
        with _conn.cursor() as cur:
            # SQL query to select a random judgment, its argument summary, and judgment date
            query = """
            SELECT j.neutral_citation, a.summary AS argument_summary, j.judgement_date
            FROM judgment j
            JOIN argument a ON j.neutral_citation = a.neutral_citation
            ORDER BY RANDOM()
            LIMIT 1;
            """
            # Execute the query
            cur.execute(query)
            result = cur.fetchone()  # Fetch the random judgment and its summary and judgment date

            if result:
                return result
            else:
                return None

    except Exception as e:
        print(f"Error: {e}")
        return None
