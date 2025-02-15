import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from main import main

@pytest.fixture
def mock_dependencies(mocker):
    """Fixture to mock all dependencies."""
    return {
        "mock_load_dotenv": mocker.patch("main.load_dotenv"),
        "mock_dashboard_title": mocker.patch("main.dashboard_title"),
        "mock_homepage_text": mocker.patch("main.homepage_text"),
        "mock_get_db_connection": mocker.patch("main.get_db_connection"),
        "mock_get_most_recent_judgments": mocker.patch("main.get_most_recent_judgments"),
        "mock_display_as_table": mocker.patch("main.display_as_table"),
        "mock_get_most_recent_judgment": mocker.patch("main.get_most_recent_judgment"),
        "mock_display_judgment": mocker.patch("main.display_judgment"),
        "mock_get_random_judgment": mocker.patch("main.get_random_judgment_with_summary_and_date"),
        "mock_st_columns": mocker.patch("streamlit.columns", return_value=(MagicMock(), MagicMock())),
        "mock_st_subheader": mocker.patch("streamlit.subheader"),
    }


def test_loads_environment(mock_dependencies):
    """Tests if environment variables are loaded."""
    main()
    mock_dependencies["mock_load_dotenv"].assert_called_once()


def test_renders_dashboard_title(mock_dependencies):
    """Tests if the dashboard title function is called."""
    main()
    mock_dependencies["mock_dashboard_title"].assert_called_once()


def test_renders_homepage_text(mock_dependencies):
    """Tests if the homepage text function is called."""
    main()
    mock_dependencies["mock_homepage_text"].assert_called_once()


def test_fetches_db_connection(mock_dependencies):
    """Tests if the database connection function is called."""
    main()
    mock_dependencies["mock_get_db_connection"].assert_called_once()


def test_fetches_and_displays_recent_judgments(mock_dependencies):
    """Tests if recent judgments are fetched and displayed in a table."""
    mock_conn = MagicMock()
    mock_dependencies["mock_get_db_connection"].return_value = mock_conn
    mock_dependencies["mock_get_most_recent_judgments"].return_value = [
        "judgment1", "judgment2"]

    main()

    mock_dependencies["mock_get_most_recent_judgments"].assert_called_once_with(
        mock_conn)
    mock_dependencies["mock_display_as_table"].assert_called_once_with(
        ["judgment1", "judgment2"])


def test_fetches_and_displays_most_recent_judgment(mock_dependencies):
    """Tests if the most recent judgment is retrieved and displayed."""
    mock_conn = MagicMock()
    mock_dependencies["mock_get_db_connection"].return_value = mock_conn
    mock_dependencies["mock_get_most_recent_judgment"].return_value = "most_recent_judgment"

    main()

    mock_dependencies["mock_get_most_recent_judgment"].assert_called_once_with(
        mock_conn)
    mock_dependencies["mock_display_judgment"].assert_any_call(
        "most_recent_judgment")


def test_fetches_and_displays_random_judgment(mock_dependencies):
    """Tests if the random judgment is retrieved and displayed."""
    mock_conn = MagicMock()
    mock_dependencies["mock_get_db_connection"].return_value = mock_conn
    mock_dependencies["mock_get_random_judgment"].return_value = "random_judgment"

    main()

    mock_dependencies["mock_get_random_judgment"].assert_called_once_with(
        mock_conn)
    mock_dependencies["mock_display_judgment"].assert_any_call(
        "random_judgment")
