"""This script gathers the data sourcing functions."""
from os import environ as ENV
from rapidfuzz import fuzz

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd
import streamlit as st
import altair as alt





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
    WHERE j.judgment_date = (SELECT MAX(judgment_date) FROM judgment)
    ORDER BY j.judgment_date DESC;
    """

    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def display_as_table(results: list) -> None:
    """Converts a list of dictionaries into a Pandas DataFrame,
    capitalises the column titles, and displays it as a table in Streamlit."""
    df = pd.DataFrame(results)

    if "court" in df.columns:
        df["court"] = df["court"].str.title()
    if "judgment_type" in df.columns:
        df["judgment_type"] = df["judgment_type"].str.title()
    if "judge" in df.columns:
        df["judge"] = df["judge"].str.title()
    
    
    
    
    df.columns = [col.replace("_", " ") for col in df.columns]
    df.columns = [col.title() for col in df.columns]

    df = df.reset_index(drop=True)
    st.subheader("New Daily Cases") 
    st.dataframe(df, hide_index=True, use_container_width=True, height=200)


def display_as_table_search(results: list) -> None:
    """Converts a list of dictionaries into a Pandas DataFrame,
    capitalises the column titles, and displays it as a table in Streamlit."""
    df = pd.DataFrame(results)

    if "court" in df.columns:
        df["court"] = df["court"].str.title()
    if "judgment_type" in df.columns:
        df["judgment_type"] = df["judgment_type"].str.title()
    if "judge" in df.columns:
        df["judge"] = df["judge"].str.title()

    df.columns = [col.replace("_", " ") for col in df.columns]
    df.columns = [col.title() for col in df.columns]

    df = df.reset_index(drop=True)
    st.subheader("Judgments")
    st.dataframe(df, hide_index=True, use_container_width=True, height=200)

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
        

        with st.expander("Read More"):
                st.text(judgment_summary)

        st.text(judgment_date)
    else:
        st.write("No judgment found.")

def cases_over_time(conn: connection):
    query = """SELECT judgment_date, judgment_type, COUNT(*) AS judgment_count
                FROM judgment
                JOIN judgment_type USING (judgment_type_id)
                GROUP BY judgment_date, judgment_type
                ORDER BY judgment_date
                """
    with conn.cursor() as cursor:
        cursor.execute(query)
        df = pd.DataFrame(cursor.fetchall())

    chart = alt.Chart(df).mark_line().encode(
        x='judgment_date:T',  # Use timestamp for x-axis
        y='judgment_count:Q',  # Numeric value for y-axis (count of judgments)
        color='judgment_type:N'  # Color the lines based on judgment_type
    ).properties(
        title="Judgment Types Over Time"
    )
    st.altair_chart(chart)

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
    """if search_query:
        filters.append(
            f"(j.neutral_citation LIKE %s OR j.judgment_summary LIKE %s)"
        )
        params.extend([f"%{search_query}%", f"%{search_query}%"])"""

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
    if search_query:
        df = df[(df['neutral_citation'].apply(match_judgments_by_citation_search, args=(search_query,)))| (df['judgment_summary'].apply(match_judgments_by_judgment_search, args=(search_query,)))]
    return df

def match_judgments_by_citation_search(df_value: str,search_query: str) -> bool:
    """Uses fuzzy matching to check if the judgment search input matches the contents of the judgments"""
    neutral_citation_score = fuzz.partial_ratio(search_query.lower(), df_value.lower())
    if neutral_citation_score > 80:
            return True
    return False

def match_judgments_by_judgment_search(df_value: str,search_query: str) -> bool:
    """Uses matching to check if the judgment search input matches the contents of the judgments"""
    search_tokens = search_query.split(' ')
    df_value = df_value.lower().split(' ')
    if all(word.lower() in df_value for word in search_tokens):
        return True
    return False


def display_judgment_search(conn: connection) -> None:
    """Displays the interface for Judgment Search Page on Streamlit."""

    search_query = st.text_input("🔍 Search a Judgment", "")

    col1, col2, col3 = st.columns([2, 1, 1])

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
        with conn.cursor() as cursor:
            cursor.execute("""SELECT 
                            MIN(judgment_date) AS min_value, 
                            MAX(judgment_date) AS max_value 
                        FROM 
                            judgment;
                        """)
            dates = cursor.fetchall()
        min_date = dates[0]['min_value']
        max_date = dates[0]['max_value']
        date_range = st.date_input("Select Date Range", value=[min_date,max_date],
                                   min_value=min_date,max_value=max_date, key="date_range")

        # If a date range is selected, extract the start and end dates
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = None, None

    # Fetch the judgments based on the selected filters
    df = fetch_judgments(conn, search_query, court_filter,
                         type_filter, start_date, end_date)
    df["court_name"] = df["court_name"].str.title()

    if not df.empty:
        display_as_table_search(df)

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
                    st.write(f"**Court:** {case_overview.get('Court')}")
                    st.write(
                        f"**Case Type:** {case_overview.get('Judgment Type')}")
                    st.write(f"**Judge(s):** {case_overview.get('Judge')}")
                    st.write(f"**In Favour of:** {case_overview.get('In Favour Of').title()}")
                else:
                    st.write("No detailed overview available.")

            with col2:
                # Fetch and display parties involved
                parties_involved = fetch_parties_involved(
                    conn, selected_citation)

                if parties_involved:
                    st.write("### Parties Involved")
                    for role in parties_involved:
                        if len(parties_involved[role]) <= 1:
                            for party in parties_involved[role]:
                                st.write(f"#### {role.title()}")
                                st.write(f"- {party.title()}")

                        elif len(parties_involved[role]) > 1:
                            st.write(f"#### {role}s")
                            for party in parties_involved[role]:
                                st.write(f"- {party.title()}")

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
            j.judge_name,
            r.role_name
        FROM judgment j
        LEFT JOIN court c ON j.court_id = c.court_id
        LEFT JOIN judgment_type jt ON j.judgment_type_id = jt.judgment_type_id
        LEFT JOIN role r ON j.in_favour_of = r.role_id
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
        "Summary": result.get('judgment_summary', "N/A"),
        "In Favour Of": result.get('role_name', "N/A")
    }


    case_overview = {
        k: v.title() if isinstance(v, str) and k != "Summary" else v
        for k, v in case_overview.items()
    }

    


    case_overview["Neutral Citation"] = case_overview["Neutral Citation"].upper()


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


