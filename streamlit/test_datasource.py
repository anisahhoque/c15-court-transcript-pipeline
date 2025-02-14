import pytest
from unittest.mock import MagicMock, patch
import data_source
import streamlit as st



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


@patch("data_source.fetch_judgments")
@patch("streamlit.text_input")
@patch("streamlit.selectbox")
@patch("streamlit.date_input")
@patch("psycopg2.connect")
def test_streamlit_input_fields(mock_connect, mock_date_input, mock_selectbox, mock_text_input, mock_fetch_judgments):
    mock_text_input.return_value = "Search term"
    mock_selectbox.side_effect = ["Court A", "Civil"]
    mock_date_input.return_value = "2025-02-01"

    mock_db_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_db_conn

    mock_fetch_judgments.return_value = [
        {"neutral_citation": "Case1", "judgement_date": "2025-01-01",
            "argument_summary": "Summary 1", "court_name": "Court A"},
        {"neutral_citation": "Case2", "judgement_date": "2025-02-01",
            "argument_summary": "Summary 2", "court_name": "Court B"}
    ]
    data_source.display_judgment_search(mock_db_conn)

    mock_fetch_judgments.assert_called_once_with(
        mock_db_conn, "Search term", "Court A", "Civil", "2025-02-01")
@patch("data_source.fetch_judgments")
@patch("streamlit.text_input")
@patch("streamlit.selectbox")
@patch("streamlit.date_input")
@patch("psycopg2.connect")
@patch("streamlit.session_state", new_callable=MagicMock)
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

    mock_fetch_judgments.return_value = [
        {"neutral_citation": "Case1", "judgement_date": "2025-01-01",
            "argument_summary": "Summary 1", "court_name": "Court A"},
        {"neutral_citation": "Case2", "judgement_date": "2025-02-01",
            "argument_summary": "Summary 2", "court_name": "Court B"}
    ]
    data_source.display_judgment_search(mock_db_conn)

    mock_fetch_judgments.assert_called_once_with(
        mock_db_conn, "Search term", "Court A", "Civil", "2025-02-01")
