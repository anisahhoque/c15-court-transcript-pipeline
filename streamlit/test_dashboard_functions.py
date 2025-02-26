import pytest
import pandas as pd
import altair as alt
import streamlit as st
from unittest.mock import MagicMock, patch
from dashboard_functions import cases_by_court, cases_by_judgment_type




@pytest.fixture
def mock_conn():
    """Mock the database connection and cursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions."""
    with patch.object(st, "altair_chart") as mock_chart:
        yield mock_chart


def test_cases_by_court(mock_conn, mock_streamlit):
    """Tests cases by court."""
    conn, cursor = mock_conn

    cursor.fetchall.return_value = [
        ("Supreme Court", 120),
        ("High Court", 85),
    ]
    df_court_cases = pd.DataFrame(
        cursor.fetchall(), columns=["Court", "Case Count"])

    df_court_cases["Court"] = df_court_cases["Court"].str.title()

    cases_by_court(conn)



def test_cases_by_judgment_type(mock_conn, mock_streamlit):
    """Tests cases by judgment type."""
    conn, cursor = mock_conn

    cursor.fetchall.return_value = [
        ("Civil", 200),
        ("Criminal", 150),
    ]

    cases_by_judgment_type(conn)
    cursor.execute.assert_called_once_with(
        """SELECT judgment_type as "Judgment Type", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN judgment_type
    ON judgment.judgment_type_id = judgment_type.judgment_type_id
    GROUP BY judgment_type"""
    )


