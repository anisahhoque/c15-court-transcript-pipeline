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

@st.cache_resource
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


@st.cache_resource
def fetch_judgments(_conn: connection, search_query="",
court=None, case_type=None, judgment_date=None) -> pd.DataFrame:
    """Returns all judgments from the database."""
    query = """
        SELECT j.neutral_citation, j.judgement_date, a.summary AS argument_summary, c.court_name
        FROM judgment j
        LEFT JOIN argument a ON j.neutral_citation = a.neutral_citation
        LEFT JOIN court c ON j.court_id = c.court_id
        WHERE 1=1
    """
    filters = []
    params = []

    if search_query:
        filters.append(
            f"(j.neutral_citation LIKE %s OR a.summary LIKE %s)"
        )
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if court and court != "All":
        filters.append("c.court_name = %s")
        params.append(court)

    if case_type and case_type != "All":
        filters.append("a.summary LIKE %s")
        params.append(f"%{case_type}%")

    if judgment_date:
        filters.append("j.judgement_date = %s")
        params.append(judgment_date)

    if filters:
        query += " AND " + " AND ".join(filters)

    with _conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

    columns = ["neutral_citation", "judgement_date",
               "argument_summary", "court_name"]
    df = pd.DataFrame(result, columns=columns)

    return df

def display_judgment_search(conn: connection) -> None:
    """Displays the interface for Judgment Search Page on Streamlit."""

    search_query = st.text_input("🔍 Search a Judgment", "")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        court_filter = st.selectbox(
            "Filter by Court", ["All", "Court A", "Court B", "Court C"]
        )

    with col2:
        type_filter = st.selectbox(
            "Filter by Type", ["All", "Civil", "Criminal", "Family", "Labor"]
        )

    with col3:
        date_filter = st.date_input("Select Date", None)

    df = fetch_judgments(conn, search_query, court_filter,
                         type_filter, date_filter)

    if not df.empty:
        st.dataframe(df, hide_index=True, use_container_width=True)

        selected_citation = st.selectbox(
            "Select a Judgment", df["neutral_citation"]
        )


        if selected_citation:
            col1, col2 = st.columns(2)  # Create two side-by-side columns

            with col1:
                case_overview = fetch_case_overview(conn, selected_citation)

                if case_overview:
                    st.write("### Case Overview")
                    for key, value in case_overview.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.write("No detailed overview available.")

            with col2:
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
    else:
        st.write("No results found for your search.")



@st.cache_resource
def fetch_case_overview(_conn:connection, neutral_citation:str) -> dict:
    """Returns the overview of a selected judgment, including the judge's title and name."""
    query = """
        SELECT 
            c.case_number,
            j.judgement_date,
            c2.court_name AS court,
            j.neutral_citation,
            j1.judge_name AS judge,
            t.title_name AS judge_title
        FROM judgment j
        LEFT JOIN "case" c ON j.neutral_citation = c.neutral_citation
        LEFT JOIN court c2 ON j.court_id = c2.court_id
        LEFT JOIN judge j1 ON j.neutral_citation = j1.neutral_citation
        LEFT JOIN title t ON j1.title_id = t.title_id
        LEFT JOIN argument a ON j.neutral_citation = a.neutral_citation
        WHERE j.neutral_citation = %s;
    """
    with _conn.cursor() as cursor:
        cursor.execute(query, (neutral_citation,))
        result = cursor.fetchone()

    if result:
        judge_full_name = f"{result.get('judge_title', 'N/A')} {result.get('judge', 'N/A')}"

        case_overview = {
            "Judgment Number": result.get('case_number', "N/A"),
            "Judgment Date": result.get('judgement_date', "N/A").strftime('%Y-%m-%d')
            if result.get('judgement_date') else "N/A",
            "Court": result.get('court', "N/A"),
            "Neutral Citation": result.get('neutral_citation', "N/A"),
            "Judge": judge_full_name
        }
        return case_overview

@st.cache_resource
def fetch_parties_involved(_conn: connection, neutral_citation: str) -> dict:
    """
    Returns a dictionary mapping role types to lists of party names.
    """
    query = """
        SELECT r.role_name, p.party_name
        FROM party p
        JOIN role r ON p.role_id = r.role_id
        JOIN "case" c ON p.case_id = c.case_id
        WHERE c.neutral_citation = %s;
    """

    parties_involved = {}

    try:
        with _conn.cursor() as cur:
            cur.execute(query, (neutral_citation,))
            results = cur.fetchall()

            # Iterate over results and populate the dictionary
            for row in results:
                role = row['role_name']
                party = row['party_name']

                if role not in parties_involved:
                    parties_involved[role] = []
                parties_involved[role].append(party)

    except Exception as e:
        print(f"Error fetching parties involved: {e}")

    return parties_involved
