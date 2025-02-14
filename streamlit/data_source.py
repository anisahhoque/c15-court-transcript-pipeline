"""This script gathers the data sourcing functions."""
from os import environ as ENV
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd
import streamlit as st




@st.cache_resource
def get_db_connection() -> connection:
    """Returns a live connection to PostgreSQL database with RealDictCursor as default."""
    config = {
        "dbname": ENV.get("DB_NAME"),
        "user": ENV.get("DB_USER"),
        "password": ENV.get("DB_PASSWORD"),
        "host": ENV.get("DB_HOST"),
        "port": ENV.get("DB_PORT"),
    }

    return connect(cursor_factory=RealDictCursor, **config)


@st.cache_resource
def get_most_recent_judgments(_conn:connection) -> list[dict]:
    """Returns the most recent cases from the database, returning them as a list of dictionaries."""

    query = """SELECT j.neutral_citation AS judgment, jd.judge_name AS judge, c.court_name as court
                FROM judgment j
                JOIN judge jd ON j.neutral_citation = jd.neutral_citation
                JOIN court c ON j.court_id = c.court_id;"""

    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()  # This will return the results as a list of dictionaries


def display_as_table(results: list) -> None:
    """Converts a list of dictionaries into a Pandas DataFrame,
    capitalises the column titles, and displays it as a table in Streamlit."""
    df = pd.DataFrame(results)

    df.columns = [col.capitalize() for col in df.columns]

    df = df.reset_index(drop=True)
    st.subheader("New Daily Cases")
    st.dataframe(df, hide_index=True, use_container_width=True)

@st.cache_resource
def get_most_recent_judgment(_conn:connection) -> dict:
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


def display_judgment(judgment_data:dict) -> None:
    """Displays data onto streamlit from passed dictionary."""
    neutral_citation = judgment_data.get("neutral_citation")
    argument_summary = judgment_data.get("argument_summary")
    judgment_date = judgment_data.get("judgement_date")

    if neutral_citation and argument_summary:
        st.subheader(neutral_citation)
        st.text(judgment_date)
        st.text(argument_summary)
    else:
        st.write("No judgment found.")

def get_random_judgment_with_summary_and_date(_conn:connection) -> dict:
    """Returns a random judgment from the database."""
    try:
        with _conn.cursor() as cur:
            query = """
            SELECT j.neutral_citation, a.summary AS argument_summary, j.judgement_date
            FROM judgment j
            JOIN argument a ON j.neutral_citation = a.neutral_citation
            ORDER BY RANDOM()
            LIMIT 1;
            """
            cur.execute(query)
            result = cur.fetchone()

            if not result:
                return None
            return result

    except Exception as e:
        print(f"Error: {e}")
        return None



def fetch_judgments(search_query="", court=None, case_type=None, judgment_date=None) -> pd.DataFrame:
    """Returns all judgments from the database."""
    conn = get_db_connection()
    query = """
        SELECT j.neutral_citation, j.judgement_date, a.summary AS argument_summary, c.court_name
        FROM judgment j
        LEFT JOIN argument a ON j.neutral_citation = a.neutral_citation
        LEFT JOIN court c ON j.court_id = c.court_id
        WHERE 1=1
    """
    filters = []
    if search_query:
        filters.append(
            f"j.neutral_citation LIKE '%{search_query}%' OR a.summary LIKE '%{search_query}%'")
    if court and court != "All":
        filters.append(f"c.court_name = '{court}'")
    if case_type and case_type != "All":
        filters.append(f"a.summary LIKE '%{case_type}%'")
    if judgment_date:
        filters.append(f"j.judgement_date = '{judgment_date}'")

    if filters:
        query += " AND " + " AND ".join(filters)

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    columns = ["neutral_citation", "judgement_date",
               "argument_summary", "court_name"]
    df = pd.DataFrame(result, columns=columns)

    return df


def display_judgment_search() -> None:
    """Displays the interface for Judgment Search Page on streamlit."""
    search_query = st.text_input("🔍 Search a Judgment", "")

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        court_filter = st.selectbox("Filter by Court", ["All", "Court A", "Court B", "Court C"])
    
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All", "Civil", "Criminal", "Family", "Labor"])
    
    with col3:
        date_filter = st.date_input("Select Date", None)

    df = fetch_judgments(search_query, court_filter, type_filter, date_filter)
    st.dataframe(df, hide_index=True, use_container_width=True)