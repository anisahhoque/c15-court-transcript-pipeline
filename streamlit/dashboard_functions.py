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
        df['judgment_date'] = pd.to_datetime(df['judgment_date'])
        min_date = df['judgment_date'].min().date()  
        max_date = df['judgment_date'].max().date()   
        selected_court = st.selectbox(
            "Select a Court", df["court_name"].unique())
        date_range = st.date_input("Select Date Range", 
                        value=[min_date, max_date],
                        min_value=min_date,
                        max_value=max_date,   
                        key="date_range")


        if len(date_range) == 2:
            start_date, end_date = date_range
            start_date = pd.to_datetime(start_date)  # Convert to datetime if it's a date or string
            end_date = pd.to_datetime(end_date)  
            df = df[(df['judgment_date'] >= start_date) & (df['judgment_date'] <= end_date)]
        else:
            start_date, end_date = None, None
        df = df[df["court_name"] == selected_court.title()]

     
        ruling_df = df.groupby('in_favour_of').size().reset_index()
        ruling_df.columns = ['ruling','count']
   
   
        chart_ruling_type = alt.Chart(ruling_df).mark_arc().encode(
            theta=alt.Theta('count', type='quantitative'),
            color=alt.Color('ruling',type='nominal')
        ).properties(title="Number of Rulings by Court")

       
        st.altair_chart(chart_ruling_type, use_container_width=True)

        st.write(f'Number of cases for the date range: {start_date.date()} - {end_date.date()} - {df.shape[0]} cases')
    else:
        st.write("No results found for your search.")