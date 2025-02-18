# dashboard_components.py
import altair as alt
import streamlit as st
import pandas as pd


def cases_by_court(conn):
    query = "SELECT court_name, COUNT(*) AS case_count FROM judgment JOIN court ON judgment.court_id = court.court_id GROUP BY court_name"

    # Execute query using connection
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Prepare data for visualization
    df_court_cases = pd.DataFrame(result)

    # Create chart using Altair
    chart_court_cases = alt.Chart(df_court_cases).mark_bar().encode(
        x='court_name',
        y='case_count',
        color='court_name',
        tooltip=['court_name', 'case_count']
    ).properties(title="Number of Cases by Court")

    # Display chart in Streamlit
    st.altair_chart(chart_court_cases, use_container_width=True)


def cases_by_judgment_type(conn):
    query = "SELECT judgment_type, COUNT(*) AS case_count FROM judgment JOIN judgment_type ON judgment.judgment_type_id = judgment_type.judgment_type_id GROUP BY judgment_type"

    # Execute query using connection
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Prepare data for visualization
    df_judgment_type = pd.DataFrame(result)

    # Create chart using Altair
    chart_judgment_type = alt.Chart(df_judgment_type).mark_arc().encode(
        theta='case_count',
        color='judgment_type',
        tooltip=['judgment_type', 'case_count']
    ).properties(title="Number of Cases by Judgment Type")

    # Display chart in Streamlit
    st.altair_chart(chart_judgment_type, use_container_width=True)
