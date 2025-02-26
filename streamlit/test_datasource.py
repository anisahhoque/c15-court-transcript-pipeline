import streamlit as st
import psycopg2
import pytest
from unittest.mock import MagicMock, patch
from data_source import (display_judgment_search, fetch_judgments,
                        fetch_case_overview, fetch_parties_involved, connect,
                        get_db_connection, get_most_recent_judgments,
                        get_most_recent_judgment, display_as_table, display_judgment,
                        get_random_judgment_with_summary_and_date
)
import pandas as pd
from datetime import datetime


import pytest
from unittest.mock import MagicMock, patch
from data_source import get_db_connection

@pytest.fixture
def mock_db_conn():
    """Mocked database connection."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = MagicMock()
    return mock_conn


def test_get_db_connection():
    """Test that get_db_connection calls connect and returns a connection."""
    with patch("data_source.connect") as mock_connect:
        conn = get_db_connection()
        mock_connect.assert_called_once()
        assert conn is not None



def test_get_most_recent_judgments(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        {"judgment": "Case123", "judge": "John Doe", "court": "Supreme Court"}]
    results = get_most_recent_judgments(mock_db_conn)
    assert results[0]["judgment"] == "Case123"
    assert results[0]["judge"] == "John Doe"
    assert results[0]["court"] == "Supreme Court"


def test_get_most_recent_judgment(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {"neutral_citation": "Case123",
                                         "argument_summary": "This is a summary", "judgement_date": "2025-01-01"}
    result = get_most_recent_judgment(mock_db_conn)
    assert result["neutral_citation"] == "Case123"
    assert result["argument_summary"] == "This is a summary"
    assert result["judgement_date"] == "2025-01-01"



def test_display_as_table():
    with patch("streamlit.dataframe") as mock_df:
        sample_data = [{"judgment": "Case123",
                        "judge": "John Doe", "court": "Supreme Court"}]
        display_as_table(sample_data)
        mock_df.assert_called_once()

def test_display_judgment():
    with patch("streamlit.html") as mock_subheader, patch("streamlit.html") as mock_text, patch("streamlit.html") as mock_write:
        judgment_data = {"neutral_citation": "Case123",
                         "judgment_summary": "This is a summary", "judgment_date": "2025-01-01"}
        display_judgment(judgment_data)
  



def test_display_judgment_no_data():
    with patch("streamlit.html") as mock_write:
        display_judgment({})
        mock_write.assert_called_once_with("<p>No judgment found.")


def test_get_random_judgment_with_summary_and_date(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {"neutral_citation": "RandomCase",
                                         "judgment_summary": "Random summary", "judgement_date": "2025-02-01"}
    result = get_random_judgment_with_summary_and_date(
        mock_db_conn)
    assert result["neutral_citation"] == "RandomCase"
    assert result["judgment_summary"] == "Random summary"
    assert result["judgement_date"] == "2025-02-01"


def test_fetch_judgments_row_count(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1"),
        ("[2022] EWCA Civ 100", "2022-05-15", "Summary 2",
         "Court of Appeal", "Judgment Type 2"),
    ]
    df = fetch_judgments(mock_db_conn)

    assert len(df) == 2


def test_fetch_judgments_specific_values(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1"),
        ("[2022] EWCA Civ 100", "2022-05-15", "Summary 2",
         "Court of Appeal", "Judgment Type 2"),
    ]
    df = fetch_judgments(mock_db_conn)
    assert df.iloc[0]["neutral_citation"] == "[2023] UKSC 10"
    assert df.iloc[1]["court_name"] == "Court of Appeal"
    assert df.iloc[0]["judgment_summary"] == "Summary 1"

def test_fetch_judgments_specific_values(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1", "Supreme Court", "Judgment Type 1"),
        ("[2022] EWCA Civ 100", "2022-05-15", "Summary 2", "Court of Appeal", "Judgment Type 2"),
    ]
    df = fetch_judgments(mock_db_conn)
    
    assert df.iloc[0]["neutral_citation"] == "[2023] UKSC 10"
    assert df.iloc[1]["court_name"] == "Court of Appeal"
    assert df.iloc[0]["judgment_summary"] == "Summary 1"


def test_fetch_judgments_column_names(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1"),
        ("[2022] EWCA Civ 100", "2022-05-15", "Summary 2",
         "Court of Appeal", "Judgment Type 2"),
    ]
    df = fetch_judgments(mock_db_conn)

    assert list(df.columns) == ["neutral_citation", "judgment_date",
                                "judgment_summary", "court_name", "judgment_type"]


def test_fetch_judgments_filter_by_court_row_count(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1")
    ]
    df = fetch_judgments(mock_db_conn, court="Supreme Court")


    assert len(df) == 1


def test_fetch_judgments_filter_by_court_name(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1")
    ]
    df = fetch_judgments(mock_db_conn, court="Supreme Court")

    assert df.iloc[0]["court_name"] == "Supreme Court"


def test_fetch_judgments_filter_by_court_values(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1",
         "Supreme Court", "Judgment Type 1")
    ]
    df = fetch_judgments(mock_db_conn, court="Supreme Court")


    assert df.iloc[0]["neutral_citation"] == "[2023] UKSC 10"
    assert df.iloc[0]["judgment_summary"] == "Summary 1"


def test_fetch_judgments_filter_by_case_type_row_count(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10",
         "Civil dispute regarding contracts", "Supreme Court", "Civil")
    ]
    df = fetch_judgments(mock_db_conn, case_type="Civil")

    assert len(df) == 1


def test_fetch_judgments_filter_by_case_type_judgment_type(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10",
         "Civil dispute regarding contracts", "Supreme Court", "Civil")
    ]
    df = fetch_judgments(mock_db_conn, case_type="Civil")

    assert "Civil" in df.iloc[0]["judgment_type"]


def test_fetch_judgments_filter_by_case_type_values(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10",
         "Civil dispute regarding contracts", "Supreme Court", "Civil")
    ]
    df = fetch_judgments(mock_db_conn, case_type="Civil")

    assert df.iloc[0]["neutral_citation"] == "[2023] UKSC 10"
    assert df.iloc[0]["court_name"] == "Supreme Court"
    assert df.iloc[0]["judgment_summary"] == "Civil dispute regarding contracts"


def test_fetch_judgments_filter_by_judgment_date(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2022] EWCA Civ 100", "2022-05-15",
         "Appeal case summary", "Court of Appeal", "Civil")
    ]
    df = fetch_judgments(
        mock_db_conn, start_date="2022-05-15", end_date="2022-05-15")

    assert len(df) == 1

    assert df.iloc[0]["judgment_date"] == "2022-05-15"




def test_fetch_judgments_empty_result(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = []
    df = fetch_judgments(mock_db_conn, court="Nonexistent Court")
    assert df.empty



@pytest.fixture
def mock_connect():
    with patch("psycopg2.connect") as mock:
        yield mock

@pytest.fixture
def mock_fetch_judgments():
    with patch("data_source.fetch_judgments") as mock:
        yield mock

@pytest.fixture
def mock_date_input():
    with patch("streamlit.date_input") as mock:
        yield mock

@pytest.fixture
def mock_selectbox():
    with patch("streamlit.selectbox") as mock:
        yield mock

@pytest.fixture
def mock_text_input():
    with patch("streamlit.text_input") as mock:
        yield mock

@pytest.fixture
def mock_session_state():
    with patch("streamlit.session_state", new_callable=MagicMock) as mock:
        yield mock

def test_fetch_judgments_called_with_correct_arguments(mock_session_state, mock_connect, mock_date_input, mock_selectbox, mock_text_input, mock_fetch_judgments):
    mock_text_input.return_value = "Search term"
    mock_selectbox.side_effect = ["Court A", "Civil"]
    mock_date_input.return_value = "2025-02-01"
    
    mock_session_state.search_query = "Search term"
    mock_session_state.court_filter = "Court A"
    mock_session_state.type_filter = "Civil"
    mock_session_state.date_filter = "2025-02-01"
    
    mock_db_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_db_conn



def test_fetch_parties_involved():
    mock_conn = MagicMock()

    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {"role_name": "Claimant", "party_name": "John Doe"},
        {"role_name": "Claimant", "party_name": "Jane Smith"},
        {"role_name": "Defendant", "party_name": "Company X"}
    ]

    result = fetch_parties_involved(mock_conn, "2025/01")

    print("Result:", result)


    expected_result = {
        "Claimant": ["John Doe", "Jane Smith"],
        "Defendant": ["Company X"]
    }

    assert result == expected_result



def test_fetch_parties_involved_with_exception(capsys):
    st.cache_data.clear()
    mock_conn = MagicMock()

    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Simulated database error")

    result = fetch_parties_involved(mock_conn, "2025/01")

    assert result == {}

    captured = capsys.readouterr()


@patch("psycopg2.connect")
def test_fetch_case_overview_success(mock_connect):
    """Test fetch_case_overview successfully retrieves case details."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.description = [
        ("neutral_citation",), ("judgment_date",), ("judgment_summary",),
        ("court_name",), ("judgment_type",), ("judge_name",)
    ]

    mock_cursor.fetchone.return_value = {
        'neutral_citation': 'Citation 1',
        'judgment_date': datetime(2025, 2, 14),
        'judgment_summary': "This is a case summary.",
        'court_name': 'Court A',
        'judgment_type': 'Civil',
        'judge_name': 'Judge 1'
    }

    mock_connect.return_value = mock_conn

    result = fetch_case_overview(mock_conn, "Citation 1")

    expected = {
        "Neutral Citation": "CITATION 1",
        "Judgment Date": "2025-02-14",
        "Court": "Court A",
        'In Favour Of': 'N/A',
        "Judgment Type": "Civil",
        "Judge": "Judge 1",
        "Summary": "This is a case summary."
    }
    
    assert result == expected
