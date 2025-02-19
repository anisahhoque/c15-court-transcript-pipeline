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
    query = """select judgment_date,judgment_summary,neutral_citation,judge_name,court_name,judgment_type, role_name as in_favour_of from judgment 
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
        df['court_name'] = df['court_name'].str.title()
        selected_court = st.selectbox(
            "Select a Court", df["court_name"].unique())

        df = df[df["court_name"] == selected_court.title()]
     
        ruling_df = df.groupby('in_favour_of').size().reset_index()
        ruling_df.columns = ['ruling','count']
   
   
        chart_ruling_type = alt.Chart(ruling_df).mark_arc().encode(
            theta=alt.Theta('count', type='quantitative'),
            color=alt.Color('ruling',type='nominal')
        ).properties(title="Number of Rulings by Court")

       
        st.altair_chart(chart_ruling_type, use_container_width=True)


