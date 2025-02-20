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
            "Select a Judgment", df["court_name"])

        if selected_court:
            col1, col2 = st.columns(2)  # Create two side-by-side columns


def display_judgments_by_judge(conn):
    """Displays a dynamic bar chart of judgments by judge with user-selected limit."""

    # Query to get the count of judgments per judge
    query = """SELECT judge_name AS "Judge", COUNT(*) AS "Total Judgments"
               FROM judgment
               GROUP BY judge_name
               ORDER BY COUNT(*) DESC;
            """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert query result to DataFrame
    df = pd.DataFrame(result, columns=["Judge", "Total Judgments"])

    # Ensure there's data before proceeding
    if df.empty:
        st.warning("No data available for judgments by judge.")
        return

    # Apply title case to judge names
    df["Judge"] = df["Judge"].str.title()

    # Get total number of judges available
    total_judges = len(df)

    # Streamlit slider for user to select the number of judges to display
    num_judges = st.slider(
        "Select number of judges to display:",
        min_value=5,
        max_value= 20,
        value=5,
        step = 5  # Default to 10 or the max available
    )

    # Filter dataframe based on user selection
    df = df.head(num_judges)

    # Create Altair bar chart
    chart = alt.Chart(df).mark_bar().encode(
        # Sort bars by descending value
        x=alt.X('Judge', title="Judge", sort="-y"),
        y=alt.Y('Total Judgments', title="No. of Total Judgments"),
        color=alt.Color('Judge', title="Judge"),
        tooltip=['Judge', 'Total Judgments']
    ).properties(title=f"Judgments by Judge (Top {num_judges})")

    # Display chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


def display_number_of_judgments_by_chamber(conn):
    query = """SELECT chamber.chamber_name AS "Chamber", COUNT(*) AS "Total Judgments"
               FROM chamber
               JOIN counsel ON chamber.chamber_id = counsel.chamber_id
               JOIN counsel_assignment ON counsel.counsel_id = counsel_assignment.counsel_id
               JOIN party ON counsel_assignment.party_id = party.party_id
               JOIN judgment ON party.neutral_citation = judgment.neutral_citation
               GROUP BY chamber.chamber_name
               ORDER BY "Total Judgments" DESC;
            """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert result into DataFrame
    df_chamber_judgments = pd.DataFrame(
        result, columns=["Chamber", "Total Judgments"])

    # Drop rows where values are 'None', 'Not Specified', NaN, empty string, or 0
    df_chamber_judgments = df_chamber_judgments[
        df_chamber_judgments["Chamber"].notna() &
        (df_chamber_judgments["Chamber"] != '') &
        (df_chamber_judgments["Chamber"].str.lower() != 'none') &
        (df_chamber_judgments["Chamber"].str.lower() != 'not specified') &
        (df_chamber_judgments["Total Judgments"].notna()) &
        (df_chamber_judgments["Total Judgments"] != 0)
    ]

    df_chamber_judgments["Chamber"] = df_chamber_judgments["Chamber"].str.title()

    # Ensure there is data before plotting
    if df_chamber_judgments.empty:
        st.warning("No valid data available for judgments by chamber.")
        return

    # Get the number of chambers to display from the user
    num_chambers = st.slider(
        "Select number of chambers to display:",
        min_value=2,
        max_value=10,
        value=2,
        step=2 # Allows selecting any value between 2 and 10
    )

    # Limit data to the selected number of chambers
    df_chamber_judgments_limited = df_chamber_judgments.head(num_chambers)

    # Create a bar chart with Altair
    chart = alt.Chart(df_chamber_judgments_limited).mark_bar().encode(
        x=alt.X('Chamber:N', title="Chamber", sort='-y'),
        y=alt.Y('Total Judgments:Q', title="No. of Total Judgments"),
        color=alt.Color('Chamber:N', title="Chamber"),
        tooltip=['Chamber', 'Total Judgments']
    ).properties(title=f"Top {num_chambers} Judgments by Chamber")

    # Display chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
