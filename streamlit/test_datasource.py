from data_source import fetch_parties_involved
from unittest.mock import MagicMock
import psycopg2
import pytest
from unittest.mock import MagicMock, patch
import data_source
import streamlit
from data_source import display_judgment_search, fetch_judgments, fetch_case_overview, fetch_parties_involved
import pandas as pd
from datetime import datetime


@pytest.fixture
def mock_db_conn():
    """Mocked database connection."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = MagicMock()
    return mock_conn


def test_get_db_connection():
    with patch("data_source.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        conn = data_source.get_db_connection()
        mock_connect.assert_called_once()
        assert conn is not None



def test_get_most_recent_judgments(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        {"judgment": "Case123", "judge": "John Doe", "court": "Supreme Court"}]
    results = data_source.get_most_recent_judgments(mock_db_conn)
    assert results[0]["judgment"] == "Case123"
    assert results[0]["judge"] == "John Doe"
    assert results[0]["court"] == "Supreme Court"


def test_get_most_recent_judgment(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {"neutral_citation": "Case123",
                                         "argument_summary": "This is a summary", "judgement_date": "2025-01-01"}
    result = data_source.get_most_recent_judgment(mock_db_conn)
    assert result["neutral_citation"] == "Case123"
    assert result["argument_summary"] == "This is a summary"
    assert result["judgement_date"] == "2025-01-01"



def test_display_as_table():
    with patch("streamlit.dataframe") as mock_df:
        sample_data = [{"judgment": "Case123",
                        "judge": "John Doe", "court": "Supreme Court"}]
        data_source.display_as_table(sample_data)
        mock_df.assert_called_once()

def test_display_judgment():
    with patch("streamlit.subheader") as mock_subheader, patch("streamlit.text") as mock_text, patch("streamlit.write") as mock_write:
        judgment_data = {"neutral_citation": "Case123",
                         "argument_summary": "This is a summary", "judgement_date": "2025-01-01"}
        data_source.display_judgment(judgment_data)
        mock_subheader.assert_called_once_with("Case123")
        mock_text.assert_any_call("2025-01-01")
        mock_text.assert_any_call("This is a summary")
        mock_write.assert_not_called()



def test_display_judgment_no_data():
    with patch("streamlit.write") as mock_write:
        data_source.display_judgment({})
        mock_write.assert_called_once_with("No judgment found.")


def test_get_random_judgment_with_summary_and_date(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {"neutral_citation": "RandomCase",
                                         "argument_summary": "Random summary", "judgement_date": "2025-02-01"}
    result = data_source.get_random_judgment_with_summary_and_date(
        mock_db_conn)
    assert result["neutral_citation"] == "RandomCase"
    assert result["argument_summary"] == "Random summary"
    assert result["judgement_date"] == "2025-02-01"



def test_fetch_judgments_no_filters(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1", "Supreme Court"),
        ("[2022] EWCA Civ 100", "2022-05-15", "Summary 2", "Court of Appeal"),
    ]
    df = data_source.fetch_judgments(mock_db_conn)
    assert len(df) == 2
    assert list(df.columns) == ["neutral_citation",
                                "judgement_date", "argument_summary", "court_name"]


def test_fetch_judgments_filter_by_court(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Summary 1", "Supreme Court")]
    df = data_source.fetch_judgments(mock_db_conn, court="Supreme Court")
    assert len(df) == 1
    assert df.iloc[0]["court_name"] == "Supreme Court"


def test_fetch_judgments_filter_by_case_type(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "Civil dispute regarding contracts", "Supreme Court")]
    df = data_source.fetch_judgments(mock_db_conn, case_type="Civil")
    assert len(df) == 1
    assert "Civil" in df.iloc[0]["argument_summary"]


def test_fetch_judgments_filter_by_judgment_date(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2022] EWCA Civ 100", "2022-05-15", "Appeal case summary", "Court of Appeal")]
    df = data_source.fetch_judgments(mock_db_conn, judgment_date="2022-05-15")
    assert len(df) == 1
    assert df.iloc[0]["judgement_date"] == "2022-05-15"

def test_fetch_judgments_search_query(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        ("[2023] UKSC 10", "2023-12-10", "This case involves criminal law", "Supreme Court")]
    df = data_source.fetch_judgments(mock_db_conn, search_query="criminal")
    assert len(df) == 1
    assert "criminal" in df.iloc[0]["argument_summary"].lower()


def test_fetch_judgments_empty_result(mock_db_conn):
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = []
    df = data_source.fetch_judgments(mock_db_conn, court="Nonexistent Court")
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
    
@patch("streamlit.text_input")
@patch("streamlit.selectbox")
@patch("streamlit.date_input")
@patch("streamlit.dataframe")
@patch("streamlit.write")
@patch("data_source.fetch_judgments")
@patch("data_source.fetch_case_overview")
def test_display_judgment_search_no_results(
    mock_fetch_case_overview, mock_fetch_judgments, mock_data_frame, mock_write,
    mock_date_input, mock_selectbox, mock_text_input
):

    mock_text_input.return_value = "Search term"
    mock_selectbox.side_effect = ["Court A", "Civil"]
    mock_date_input.return_value = None
    
    mock_fetch_judgments.return_value = pd.DataFrame()
    mock_db_conn = MagicMock()

    display_judgment_search(mock_db_conn)

    mock_data_frame.assert_called_once()


@patch("streamlit.text_input")
@patch("streamlit.selectbox")
@patch("streamlit.date_input")
@patch("streamlit.dataframe")
@patch("streamlit.write") 
@patch("data_source.fetch_judgments")
@patch("data_source.fetch_case_overview")
def test_display_judgment_search_with_results(
    mock_fetch_case_overview, mock_fetch_judgments, mock_data_frame, mock_write,
    mock_date_input, mock_selectbox, mock_text_input
):

    # Mocking Streamlit inputs
    mock_text_input.return_value = "Search term"
    mock_selectbox.return_value = "Citation 1"
    mock_date_input.return_value = None

    df = pd.DataFrame({
        "neutral_citation": ["Citation 1", "Citation 2"],
        "court_name": ["Court A", "Court B"],
        "judgment_name": ["Judgment 1", "Judgment 2"]
    })
    mock_fetch_judgments.return_value = df
    mock_fetch_case_overview.return_value = {
        "Court Name": "Court A",
        "Judgment Name": "Judgment 1",
        "Judgment Date": "2025-02-14",
        "Presiding Judge(s)": "Judge 1"
    }

    mock_db_conn = MagicMock()

    display_judgment_search(mock_db_conn)



@patch("psycopg2.connect")
def test_fetch_case_overview_success(mock_connect):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_row = {
        'case_number': '12345',
        'judgement_date': datetime(2025, 2, 14),
        'court': 'Court A',
        'neutral_citation': 'Citation 1',
        'judge': 'Judge 1',
        'judge_title': 'Mr.'
    }
    mock_cursor.fetchone.return_value = mock_row

    mock_connect.return_value = mock_conn

    result = fetch_case_overview(mock_conn, "Citation 1")

    expected = {
        "Judgment Number": "12345",
        "Judgment Date": "2025-02-14",
        "Court": "Court A",
        "Neutral Citation": "Citation 1",
        "Judge": "Mr. Judge 1"
    }

    assert result == expected


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
    streamlit.cache_data.clear()
    mock_conn = MagicMock()

    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Simulated database error")

    result = fetch_parties_involved(mock_conn, "2025/01")

    assert result == {}

    captured = capsys.readouterr()


