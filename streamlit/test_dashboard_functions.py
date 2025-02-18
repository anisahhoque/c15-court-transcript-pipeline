
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

    cases_by_court(conn)

    # Verify SQL execution
    cursor.execute.assert_called_once_with(
        "SELECT court_name, COUNT(*) AS case_count FROM judgment "
        "JOIN court ON judgment.court_id = court.court_id GROUP BY court_name"
    )

    # Verify DataFrame creation
    expected_df = pd.DataFrame(
        [("Supreme Court", 120), ("High Court", 85)], columns=["court_name", "case_count"]
    )
    assert isinstance(expected_df, pd.DataFrame)

    # Ensure Streamlit was called with an Altair chart
    args, kwargs = mock_streamlit.call_args
    # Ensure first argument is an Altair chart
    assert isinstance(args[0], alt.Chart)
    # Ensure correct argument is passed
    assert kwargs.get("use_container_width") is True


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

    cases_by_judgment_type(conn)

    # Verify SQL execution
    cursor.execute.assert_called_once_with(
        "SELECT judgment_type, COUNT(*) AS case_count FROM judgment "
        "JOIN judgment_type ON judgment.judgment_type_id = judgment_type.judgment_type_id GROUP BY judgment_type"
    )

    # Verify DataFrame creation
    expected_df = pd.DataFrame(
        [("Civil", 200), ("Criminal", 150)], columns=["judgment_type", "case_count"]
    )
    assert isinstance(expected_df, pd.DataFrame)

    # Ensure Streamlit was called with an Altair chart
    args, kwargs = mock_streamlit.call_args
    # Ensure first argument is an Altair chart
    assert isinstance(args[0], alt.Chart)
    # Ensure correct argument is passed
    assert kwargs.get("use_container_width") is True
