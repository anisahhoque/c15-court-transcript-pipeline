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
def get_most_recent_judgments(_conn: connection) -> list[tuple]:
    """Returns the most recent cases from the database, returning them as a list of tuples."""

    query = """
    SELECT 
        j.neutral_citation AS judgment, 
        j.judge_name AS judge, 
        c.court_name AS court,
        jt.judgment_type AS judgment_type
    FROM judgment j
    JOIN court c ON j.court_id = c.court_id
    JOIN judgment_type jt ON j.judgment_type_id = jt.judgment_type_id
    ORDER BY j.judgment_date DESC;
    """

    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def display_as_table(results: list) -> None:
    """Converts a list of dictionaries into a Pandas DataFrame,
    capitalises the column titles, and displays it as a table in Streamlit."""
    df = pd.DataFrame(results)

    df.columns = [col.capitalize() for col in df.columns]

    df = df.reset_index(drop=True)
    st.subheader("New Daily Cases")
    st.dataframe(df, hide_index=True, use_container_width=True)

@st.cache_resource
def get_most_recent_judgment(_conn: connection) -> dict:
    """Returns the latest judgment with details."""    
    query = """
    SELECT
        j.neutral_citation, 
        j.court_id, 
        j.judgment_date, 
        j.judgment_summary
    FROM 
        judgment j
    ORDER BY 
        j.judgment_date DESC
    LIMIT 1;
    """
    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchone()  # Returns the latest judgment record




def display_judgment(judgment_data:dict) -> None:
    """Displays data onto streamlit from passed dictionary."""
    neutral_citation = judgment_data.get("neutral_citation")
    judgment_summary = judgment_data.get("judgment_summary")
    judgment_date = judgment_data.get("judgment_date")

    if neutral_citation and judgment_summary:
        st.subheader(neutral_citation)
        st.text(judgment_summary)
        st.text(judgment_date)
    else:
        st.write("No judgment found.")


@st.cache_resource(ttl=86400)
def get_random_judgment_with_summary_and_date(_conn: connection) -> dict:
    """Returns a random judgment from the database each day."""
    try:
        with _conn.cursor() as cur:
            query = """
            SELECT 
                j.neutral_citation, 
                j.judgment_summary, 
                j.judgment_date
            FROM 
                judgment j
            ORDER BY 
                RANDOM()
            LIMIT 1;
            """
            cur.execute(query)
            result = cur.fetchone()

            if result:
                return result

    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_judgments(_conn: connection, search_query="", court=None,
case_type=None, start_date=None, end_date=None) -> pd.DataFrame:
    """Returns filtered judgments from the database."""
    query = """
        SELECT j.neutral_citation, j.judgment_date, 
               j.judgment_summary AS judgment_summary,  -- Truncated summary with "..."
               c.court_name, jt.judgment_type, j.judgment_summary AS full_judgment_summary
        FROM judgment j
        LEFT JOIN court c ON j.court_id = c.court_id
        LEFT JOIN judgment_type jt ON j.judgment_type_id = jt.judgment_type_id
        WHERE 1=1
    """
    filters = []
    params = []

    # Full-text search query, including the judgment summary
    if search_query:
        filters.append(
            f"(j.neutral_citation LIKE %s OR j.judgment_summary LIKE %s)"
        )
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if court and court != "All":
        filters.append("c.court_name = %s")
        params.append(court)

    if case_type and case_type != "All":
        filters.append("jt.judgment_type LIKE %s")
        params.append(f"%{case_type}%")

    if start_date and end_date:
        filters.append("j.judgment_date BETWEEN %s AND %s")
        params.extend([start_date, end_date])

    if filters:
        query += " AND " + " AND ".join(filters)

    with _conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

    columns = ["neutral_citation", "judgment_date",
               "judgment_summary", "court_name", "judgment_type"]
    df = pd.DataFrame(result, columns=columns)

    return df


def display_judgment_search(conn: connection) -> None:
    """Displays the interface for Judgment Search Page on Streamlit."""

    search_query = st.text_input("🔍 Search a Judgment", "")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # Fetch courts dynamically from the database
        query = "SELECT DISTINCT court_name FROM court"
        with conn.cursor() as cursor:
            cursor.execute(query)
            court_names = [row["court_name"] for row in cursor.fetchall()]

        # "All" as a default option
        court_names.insert(0, "All")

        court_filter = st.selectbox("Filter by Court", court_names)

    with col2:
        type_filter = st.selectbox(
            "Filter by Type", ["All", "Civil", "Criminal"])

    with col3:
        date_range = st.date_input("Select Date Range", [], key="date_range")

        # If a date range is selected, extract the start and end dates
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = None, None

    # Fetch the judgments based on the selected filters
    df = fetch_judgments(conn, search_query, court_filter,
                         type_filter, start_date, end_date)

    if not df.empty:
        st.dataframe(df, hide_index=True, use_container_width=True)

        selected_citation = st.selectbox(
            "Select a Judgment", df["neutral_citation"])

        if selected_citation:
            col1, col2 = st.columns(2)  # Create two side-by-side columns

            with col1:
                case_overview = fetch_case_overview(conn, selected_citation)

                if case_overview:
                    st.write("### Case Overview")
                    st.write(
                        f"**Neutral Citation:** {case_overview.get('Neutral Citation')}")
                    st.write(
                        f"**Judgment Date:** {case_overview.get('Judgment Date')}")
                    st.write(f"**Court Name:** {case_overview.get('Court')}")
                    st.write(
                        f"**Judgment Type:** {case_overview.get('Judgment Type')}")
                    st.write(f"**Judge(s):** {case_overview.get('Judge')}")
                else:
                    st.write("No detailed overview available.")

            with col2:
                # Fetch and display parties involved
                parties_involved = fetch_parties_involved(
                    conn, selected_citation)

                if parties_involved:
                    st.write("### Parties Involved")
                    for role, names in parties_involved.items():
                        st.write(f"#### {role}(s)")  # Dynamic role heading
                        for name in names:
                            st.write(f"- {name}")
                else:
                    st.write("No party information available.")

            # Display the full judgment summary
            judgment_summary = case_overview["Summary"]
            st.write("### Full Judgment Summary")
            st.write(judgment_summary)

    else:
        st.write("No results found for your search.")


def fetch_case_overview(conn: connection, neutral_citation: str) -> dict:
    """Returns the overview of a selected judgment."""
    query = """
        SELECT 
            j.neutral_citation,
            j.judgment_date,
            j.judgment_summary,
            c.court_name,
            jt.judgment_type,
            j.judge_name
        FROM judgment j
        LEFT JOIN court c ON j.court_id = c.court_id
        LEFT JOIN judgment_type jt ON j.judgment_type_id = jt.judgment_type_id
        WHERE j.neutral_citation = %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (neutral_citation,))
        result = cursor.fetchone()

    if not result:
        return None
    case_overview = {
        "Neutral Citation": result.get('neutral_citation', "N/A"),
        "Judgment Date": result.get('judgment_date', "N/A").strftime('%Y-%m-%d')
        if result.get('judgment_date') else "N/A",
        "Court": result.get('court_name', "N/A"),
        "Judgment Type": result.get('judgment_type', "N/A"),
        "Judge": result.get('judge_name', "N/A"),
        "Summary": result.get('judgment_summary', "N/A")
    }
    return case_overview

def fetch_parties_involved(_conn: connection, neutral_citation: str) -> dict:
    """
    Returns a dictionary mapping role types to lists of party names.
    """
    query = """SELECT r.role_name, p.party_name
        FROM party p
        JOIN role r ON p.role_id = r.role_id
        JOIN judgment j ON p.neutral_citation = j.neutral_citation
        WHERE j.neutral_citation = %s"""

    parties_involved = {}

    try:
        with _conn.cursor() as cur:
            cur.execute(query, (neutral_citation,))
            results = cur.fetchall()
            for row in results:
                role = row['role_name']
                party = row['party_name']

                if role not in parties_involved:
                    parties_involved[role] = []
                parties_involved[role].append(party)


    except Exception as e:
        print(f"Error fetching parties involved: {e}")

    return parties_involved



