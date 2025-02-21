import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from Home import main

@pytest.fixture
def mock_dependencies(mocker):
    """Fixture to mock all dependencies."""
    return {
        "mock_load_dotenv": mocker.patch("Home.load_dotenv"),
        "mock_dashboard_title": mocker.patch("Home.dashboard_title"),
        "mock_homepage_text": mocker.patch("Home.homepage_text"),
        "mock_get_db_connection": mocker.patch("Home.get_db_connection"),
        "mock_get_most_recent_judgments": mocker.patch("Home.get_most_recent_judgments"),
        "mock_display_as_table": mocker.patch("Home.display_as_table"),
        "mock_get_most_recent_judgment": mocker.patch("Home.get_most_recent_judgment"),
        "mock_display_judgment": mocker.patch("Home.display_judgment"),
        "mock_get_random_judgment": mocker.patch("Home.get_random_judgment_with_summary_and_date"),
        "mock_st_columns": mocker.patch("streamlit.columns", return_value=(MagicMock(), MagicMock())),
        "mock_st_subheader": mocker.patch("streamlit.subheader"),
        "mock_cases_by_court": mocker.patch("Home.cases_by_court"),
        "mock_cases_by_judgment_type": mocker.patch("Home.cases_by_judgment_type"),
        "mock_cases_over_time":mocker.patch("Home.cases_over_time")
    }


def test_loads_environment(mock_dependencies):
    """Tests if environment variables are loaded."""
    main()
    mock_dependencies["mock_load_dotenv"].assert_called_once()


def test_renders_dashboard_title(mock_dependencies):
    """Tests if the dashboard title function is called."""
    main()
    mock_dependencies["mock_dashboard_title"].assert_called_once()

def test_cases_by_court(mock_dependencies):
    main()
    mock_dependencies["mock_cases_by_court"].assert_called_once()

def test_cases_by_judgment_type(mock_dependencies):
    main()
    mock_dependencies["mock_cases_by_judgment_type"].assert_called_once()

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
