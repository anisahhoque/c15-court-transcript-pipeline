import pytest
from unittest.mock import patch, MagicMock
import data_source


@pytest.fixture
def mock_db_conn():
    """Mocked database connection."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = MagicMock()
    return mock_conn


def test_get_db_connection():
    """Test if get_db_connection establishes a PostgreSQL connection."""
    with patch("data_source.connect") as mock_connect:
        mock_connect.return_value = MagicMock()  # Mock connection object

        conn = data_source.get_db_connection()

        mock_connect.assert_called_once()
        assert conn is not None


def test_get_most_recent_judgments(mock_db_conn):
    """Test retrieving most recent judgments."""
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        {"judgment": "Case123", "judge": "John Doe", "court": "Supreme Court"}
    ]

    results = data_source.get_most_recent_judgments(mock_db_conn)

    assert isinstance(results, list)
    assert results[0]["judgment"] == "Case123"
    assert results[0]["judge"] == "John Doe"
    assert results[0]["court"] == "Supreme Court"


def test_display_as_table():
    """Test if display_as_table correctly displays data in Streamlit."""
    with patch("streamlit.dataframe") as mock_df:
        sample_data = [{"judgment": "Case123",
                        "judge": "John Doe", "court": "Supreme Court"}]
        data_source.display_as_table(sample_data)

        mock_df.assert_called_once()


def test_get_most_recent_judgment(mock_db_conn):
    """Test retrieving the most recent judgment."""
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {
        "neutral_citation": "Case123",
        "argument_summary": "This is a summary",
        "judgement_date": "2025-01-01"
    }

    result = data_source.get_most_recent_judgment(mock_db_conn)

    assert isinstance(result, dict)
    assert result["neutral_citation"] == "Case123"
    assert result["argument_summary"] == "This is a summary"
    assert result["judgement_date"] == "2025-01-01"


def test_display_judgment():
    """Test if display_judgment correctly displays judgment details."""
    with patch("streamlit.subheader") as mock_subheader, \
            patch("streamlit.text") as mock_text, \
            patch("streamlit.write") as mock_write:

        judgment_data = {
            "neutral_citation": "Case123",
            "argument_summary": "This is a summary",
            "judgement_date": "2025-01-01"
        }

        data_source.display_judgment(judgment_data)

        mock_subheader.assert_called_once_with("Case123")
        mock_text.assert_any_call("2025-01-01")
        mock_text.assert_any_call("This is a summary")
        mock_write.assert_not_called()


def test_display_judgment_no_data():
    """Test display_judgment with empty data."""
    with patch("streamlit.write") as mock_write:
        data_source.display_judgment({})  # Empty dictionary

        mock_write.assert_called_once_with("No judgment found.")


def test_get_random_judgment_with_summary_and_date(mock_db_conn):
    """Test retrieving a random judgment."""
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {
        "neutral_citation": "RandomCase",
        "argument_summary": "Random summary",
        "judgement_date": "2025-02-01"
    }

    result = data_source.get_random_judgment_with_summary_and_date(
        mock_db_conn)

    assert isinstance(result, dict)
    assert result["neutral_citation"] == "RandomCase"
    assert result["argument_summary"] == "Random summary"
    assert result["judgement_date"] == "2025-02-01"


def test_get_random_judgment_with_summary_and_date_empty(mock_db_conn):
    """Test retrieving a random judgment when no data is found."""
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = None

    result = data_source.get_random_judgment_with_summary_and_date(
        mock_db_conn)

    assert result is None


def test_get_random_judgment_with_summary_and_date_exception(mock_db_conn):
    """Test handling an exception in get_random_judgment_with_summary_and_date."""
    mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
    mock_cursor.execute.side_effect = Exception("Database error")

    result = data_source.get_random_judgment_with_summary_and_date(
        mock_db_conn)

    assert result is None  # Should gracefully return None instead of crashing
