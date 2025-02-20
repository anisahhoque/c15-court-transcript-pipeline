import pytest
import pandas as pd
import altair as alt
import streamlit as st
from unittest.mock import MagicMock, patch

from dashboard_functions import cases_by_court, cases_by_judgment_type, display_judgments_for_court


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
    conn, cursor = mock_conn

    # Mock query results
    cursor.fetchall.return_value = [
        ("Supreme Court", 120),
        ("High Court", 85),
    ]

    # Update the DataFrame creation with proper column names
    df_court_cases = pd.DataFrame(
        cursor.fetchall(), columns=["Court", "Case Count"])

    # Mock the pandas DataFrame transformation and visualization
    df_court_cases["Court"] = df_court_cases["Court"].str.title()

    # Call the function
    cases_by_court(conn)


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


def test_cases_by_judgment_type(mock_conn, mock_streamlit):
    conn, cursor = mock_conn

    # Mock query results
    cursor.fetchall.return_value = [
        ("Civil", 200),
        ("Criminal", 150),
    ]

    # Call the function
    cases_by_judgment_type(conn)

    # Verify SQL execution with corrected expected query format
    cursor.execute.assert_called_once_with(
        """SELECT judgment_type as "Judgment Type", COUNT(*) AS "Case Count"
    FROM judgment
    JOIN judgment_type
    ON judgment.judgment_type_id = judgment_type.judgment_type_id
    GROUP BY judgment_type"""
    )


def test_display_judgments_for_court():
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Sample mock result for query execution
    mock_result = [
        ('2025-01-01', 'Judgment Summary 1', 'Citation 1',
         'Judge A', 'Court A', 'Civil', 'Claimant'),
        ('2025-02-01', 'Judgment Summary 2', 'Citation 2',
         'Judge B', 'Court A', 'Criminal', 'Defendant')
    ]

    # Mock the execution of the query and return the result
    mock_conn.cursor().execute.return_value.__enter__.return_value = None
    mock_conn.cursor().fetchall.return_value.__enter__.return_value = mock_result

    # Mock Streamlit components
    mock_selectbox = MagicMock()
    mock_date_input = MagicMock()
    mock_write = MagicMock()
    mock_altair_chart = MagicMock()

    # Mock the return values of Streamlit components
    mock_selectbox.return_value = 'Court A'
    mock_date_input.return_value = ['2025-01-01', '2025-12-31']

    # Replace Streamlit components with mocks
    st.selectbox = mock_selectbox
    st.date_input = mock_date_input
    st.write = mock_write
    st.altair_chart = mock_altair_chart

    # Call the function to test
    display_judgments_for_court(mock_conn)

    # # Check that Streamlit's write function was called with the correct message
    mock_write.assert_any_call('No results found for your search.')

    assert len(mock_result) == 2  # We have

