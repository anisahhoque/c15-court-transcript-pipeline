"""This script has the supportive functions for the analytics board."""
import pandas as pd
import altair as alt
from psycopg2 import connect as connection
import streamlit as st


def cases_by_court(conn: connection) -> None:
    """Returns cases by court chart diagram."""
    query = """SELECT court_name as "Court", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN court ON judgment.court_id = court.court_id
    GROUP BY "Court"
    ORDER BY "Case Count" DESC
    LIMIT 10;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    df_court_cases = pd.DataFrame(result, columns=["Court", "Case Count"])
    df_court_cases["Court"] = df_court_cases["Court"].str.title()

    
    chart_court_cases = alt.Chart(df_court_cases).mark_bar().encode(
        y=alt.Y('Court', title=None, sort="-x",
                axis=alt.Axis(labelLimit=500)),
        x=alt.X('Case Count', title="No. of Total Judgments"),
        color=alt.Color('Court', title=None, legend=None),
        tooltip=['Court', 'Case Count']
    ).properties(title="Number of Judgments by Court")


    st.altair_chart(chart_court_cases, use_container_width=True)


def cases_by_judgment_type(conn: connection) -> None:
    """Displays cases by judgment type in a pie chart on streamlit."""
    query = """SELECT judgment_type as "Judgment Type", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN judgment_type
    ON judgment.judgment_type_id = judgment_type.judgment_type_id
    GROUP BY judgment_type"""


    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()


    df_judgment_type = pd.DataFrame(
        result, columns=["Judgment Type", "Case Count"])
    df_judgment_type["Judgment Type"] = df_judgment_type["Judgment Type"].str.title()


    chart_judgment_type = alt.Chart(df_judgment_type).mark_arc().encode(
        theta=alt.Theta('Case Count', title="Types"),
        color=alt.Color('Judgment Type', title="Types"),
        tooltip=['Judgment Type', 'Case Count']
    ).properties(title="Number of Judgments by Judgment Type")

    st.altair_chart(chart_judgment_type, use_container_width=True)





def adjust_sidebar_width(width=200):
    """Adjusts the sidebar width in Streamlit and displays a centered image."""
    image_url = """https://github.com/anisahhoque/c15-court-transcript-pipeline/blob/main/dev-resources/s-blob-v1-IMAGE-iD349-cbH2c.png?raw=true"""

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            width: {width}px !important;
        }}
        </style>
        <div style="padding: 10px; text-align: center;">
            <img src="{image_url}" width="20%" alt="Sidebar Image"/>
        </div>
        """,
        unsafe_allow_html=True
    )

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

