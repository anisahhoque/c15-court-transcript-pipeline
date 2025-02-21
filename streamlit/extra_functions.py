import pandas as pd
import streamlit as st
import altair as alt
from psycopg2 import connect as connection
def get_judgment_data(chamber_id, conn):
    query = """
        SELECT 
            COUNT(j.neutral_citation) AS total_judgments,
            SUM(CASE WHEN jt.judgment_type = 'criminal' THEN 1 ELSE 0 END) AS criminal_judgments,
            SUM(CASE WHEN jt.judgment_type = 'civil' THEN 1 ELSE 0 END) AS civil_judgments
        FROM chamber c
        LEFT JOIN counsel co ON c.chamber_id = co.chamber_id
        LEFT JOIN counsel_assignment ca ON co.counsel_id = ca.counsel_id
        LEFT JOIN party p ON ca.party_id = p.party_id
        LEFT JOIN judgment j ON p.neutral_citation = j.neutral_citation
        LEFT JOIN judgment_type jt ON j.judgment_type_id = jt.judgment_type_id
        WHERE c.chamber_id = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (chamber_id,))
        result = cursor.fetchone()

    return pd.DataFrame([result]) if result else pd.DataFrame(columns=["total_judgments", "criminal_judgments", "civil_judgments"])


def compare_chambers(conn):
    # Fetch available chambers
    with conn.cursor() as cursor:
        cursor.execute("SELECT chamber_id, chamber_name FROM chamber")
        result = cursor.fetchall()

    df = pd.DataFrame(result)
    df["chamber_name"] = df["chamber_name"].astype(str).str.strip()
    invalid_values = ["", "none", "null", "not specified", "na"]
    df_cleaned = df[~df["chamber_name"].str.lower().isin(invalid_values)]

    # Use .loc[] to modify the "chamber_name" column in the cleaned DataFrame
    df_cleaned.loc[:, "chamber_name"] = df_cleaned["chamber_name"].str.title()

    # Create the name-to-ID mapping
    chamber_options = dict(
        zip(df_cleaned["chamber_name"], df_cleaned["chamber_id"]))

    # Select the first chamber
    chamber_names = list(chamber_options.keys())
    chamber_1_name = st.selectbox(
        "Select first chamber", chamber_names, index=0)  # Default to the first chamber

    # Remove the selected first chamber from the list for the second selectbox
    remaining_chamber_names = [
        name for name in chamber_names if name != chamber_1_name]

    # Select the second chamber (from remaining options)
    chamber_2_name = st.selectbox(
        # Default to the first remaining option
        "Select second chamber", remaining_chamber_names, index=0)

    # Get the chamber IDs based on selected chamber names
    chamber_1_id = chamber_options[chamber_1_name]
    chamber_2_id = chamber_options[chamber_2_name]

    # Get the metrics for both chambers
    chamber_1_data = get_judgment_data(chamber_1_id, conn)
    chamber_2_data = get_judgment_data(chamber_2_id, conn)

    # Add Chamber names for clarity in visualizations
    chamber_1_data["Chamber"] = chamber_1_name
    chamber_2_data["Chamber"] = chamber_2_name

    # Combine the data
    comparison_df = pd.concat([chamber_1_data, chamber_2_data])

    st.subheader("Chambers Comparison")

    # Display Judgment Count Comparison in a separate row
    with st.container():
        st.write("#### Judgment Count Comparison")
        judgment_chart = alt.Chart(comparison_df).mark_bar().encode(
            y=alt.Y("Chamber:N", title=None,
                    axis=alt.Axis(labelLimit=300)),
            x=alt.X("total_judgments:Q", title="Total Judgments"),
            color="Chamber:N"
        ).properties(title="Total Judgment Count Comparison")
        st.altair_chart(judgment_chart, use_container_width=True)

    # Display Criminal Judgment Comparison in a separate row
    with st.container():
        st.write("#### Criminal Judgment Comparison")
        criminal_chart = alt.Chart(comparison_df).mark_bar().encode(
            y=alt.Y("Chamber:N", title=None,
                    axis=alt.Axis(labelLimit=300)),
            x=alt.X("criminal_judgments:Q", title="Criminal Judgments"),
            color="Chamber:N"
        ).properties(title="Criminal Judgment Count Comparison")
        st.altair_chart(criminal_chart, use_container_width=True)

    # Display Civil Judgment Comparison in a separate row
    with st.container():
        st.write("#### Civil Judgment Comparison")
        civil_chart = alt.Chart(comparison_df).mark_bar().encode(
            y=alt.Y("Chamber:N", title=None,
                    axis=alt.Axis(labelLimit=300)),
            x=alt.X("civil_judgments:Q", title="Civil Judgments"),
            color="Chamber:N"
        ).properties(title="Civil Judgment Count Comparison")
        st.altair_chart(civil_chart, use_container_width=True)


def display_judgments_for_court(conn: connection) -> None:
    """Displays the judgments for a given court"""
    query = """select judgment_date,judgment_summary,neutral_citation,
                    judge_name,court_name,judgment_type,
                    role_name as in_favour_of from judgment 
                    join court using (court_id)
                    join judgment_type
                    using (judgment_type_id)
                    join role r on judgment.in_favour_of = r.role_id """

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
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['judgment_date'] >= start_date)
                    & (df['judgment_date'] <= end_date)]
        else:
            start_date, end_date = None, None
        df = df[df["court_name"] == selected_court.title()]

        df['in_favour_of'] = df['in_favour_of'].str.title()
        ruling_df = df.groupby('in_favour_of').size().reset_index()
        ruling_df.columns = ['Ruling', 'Count']

        chart_ruling_type = alt.Chart(ruling_df).mark_arc().encode(
            theta=alt.Theta('Count', type='quantitative'),
            color=alt.Color('Ruling', type='nominal')
        ).properties(title="Number of Rulings by Court")
        st.write(f'Cases found: {df.shape[0]}')
        st.altair_chart(chart_ruling_type, use_container_width=True)

    else:
        st.write("No results found for your search.")


def display_judgments_by_judge(conn):
    """Displays a dynamic bar chart of judgments by judge with user-selected limit."""

    query = """SELECT judge_name AS "Judge", COUNT(*) AS "Total Judgments"
               FROM judgment
               GROUP BY judge_name
               ORDER BY COUNT(*) DESC;
            """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    df = pd.DataFrame(result, columns=["Judge", "Total Judgments"])

    if df.empty:
        st.warning("No data available for judgments by judge.")
        return

    df["Judge"] = df["Judge"].str.title()

    st.subheader("Judgments by Judge")

    num_judges = st.slider(
        "Select number of judges to display:",
        min_value=5,
        max_value=20,
        value=5,
        step=5
    )

    df = df.head(num_judges)

    chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Judge', title=None, sort="-x",
                axis=alt.Axis(labelLimit=300)),
        x=alt.X('Total Judgments', title="No. of Total Judgments"),
        color=alt.Color('Judge', title="Judge", legend=None),
        tooltip=['Judge', 'Total Judgments']
    ).properties(title=f"Top {num_judges}")

    st.altair_chart(chart, use_container_width=True)


def display_number_of_judgments_by_chamber(conn):
    """Displays the a graph showing number of judgments by the chamber"""
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

    df_chamber_judgments = pd.DataFrame(
        result, columns=["Chamber", "Total Judgments"])

    df_chamber_judgments = df_chamber_judgments[
        df_chamber_judgments["Chamber"].notna() &
        (df_chamber_judgments["Chamber"] != '') &
        (df_chamber_judgments["Chamber"].str.lower() != 'none') &
        (df_chamber_judgments["Chamber"].str.lower() != 'not specified') &
        (df_chamber_judgments["Total Judgments"].notna()) &
        (df_chamber_judgments["Total Judgments"] != 0)
    ]

    df_chamber_judgments["Chamber"] = df_chamber_judgments["Chamber"].str.title()

    if df_chamber_judgments.empty:
        st.warning("No valid data available for judgments by chamber.")
        return

    st.subheader("Judgments by Chamber")

    num_chambers = st.slider(
        "Select number of chambers to display:",
        min_value=2,
        max_value=10,
        value=2,
        step=2
    )

    df_chamber_judgments_limited = df_chamber_judgments.head(num_chambers)

    chart = alt.Chart(df_chamber_judgments_limited).mark_bar().encode(
        y=alt.Y('Chamber:N', title=None, sort='-x',
                axis=alt.Axis(labelLimit=300)),
        x=alt.X('Total Judgments:Q', title="No. of Total Judgments"),
        color=alt.Color('Chamber:N', title="Chamber", legend=None),
        tooltip=['Chamber', 'Total Judgments']
    ).properties(title=f"Top {num_chambers}")

    st.altair_chart(chart, use_container_width=True)
