"""This script has the supportive functions for the analytics board."""
import pandas as pd
import altair as alt
from psycopg2 import connect as connection
import streamlit as st
from data_source import fetch_case_overview, fetch_parties_involved

def cases_by_court(conn:connection) -> None:
    """Returns cases by court chart diagram."""
    query = """SELECT court_name as "Court", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN court ON judgment.court_id = court.court_id
    GROUP BY "Court"
    ORDER BY "Case Count" DESC
    LIMIT 10;
    """

    # Execute query using connection
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Prepare data for visualization
    df_court_cases = pd.DataFrame(result)
    df_court_cases["Court"] = df_court_cases["Court"].str.title()

    # Create chart using Altair
    chart_court_cases = alt.Chart(df_court_cases).mark_bar().encode(
        x=alt.X('Court', title="Court Name", sort="-y"),
        y=alt.Y('Case Count', title="No. of Total Judgments"),
        color=alt.Color('Court', title = "Courts"),
        tooltip=['Court', 'Case Count']
    ).properties(title="Number of Judgments by Court")

    # Display chart in Streamlit
    st.altair_chart(chart_court_cases, use_container_width=True)


def cases_by_judgment_type(conn:connection) -> None:
    """Displays cases by judgment type in a pie chart on streamlit."""
    query = """SELECT judgment_type as "Judgment Type", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN judgment_type
    ON judgment.judgment_type_id = judgment_type.judgment_type_id
    GROUP BY judgment_type"""

    # Execute query using connection
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Prepare data for visualization
    df_judgment_type = pd.DataFrame(result)
    df_judgment_type["Judgment Type"] = df_judgment_type["Judgment Type"].str.title()

    # Create chart using Altair
    chart_judgment_type = alt.Chart(df_judgment_type).mark_arc().encode(
        theta=alt.Theta('Case Count', title="Types"),
        color=alt.Color('Judgment Type', title="Types"),
        tooltip=['Judgment Type', 'Case Count']
    ).properties(title="Number of Judgments by Judgment Type")

    # Display chart in Streamlit
    st.altair_chart(chart_judgment_type, use_container_width=True)


def display_judgments_for_court(conn: connection) -> None:
    query = """select * from judgment 
    join court using (court_id)
    join judgment_type
    using (judgment_type_id)
    join role r on judgment.in_favour_of = r.role_id 
    """

    
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)


    if not df.empty:
        selected_court = st.selectbox(
            "Select a Judgment", df["court_name"])

        if selected_court:
            col1, col2 = st.columns(2)  # Create two side-by-side columns



