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


