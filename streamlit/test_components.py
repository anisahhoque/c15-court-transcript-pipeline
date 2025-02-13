import pytest
import streamlit as st
from unittest.mock import patch
from main import dashboard_title 



@pytest.fixture
def mock_sidebar_radio():
    with patch.object(st.sidebar, "radio") as mock_radio:
        yield mock_radio


def test_dashboard_title(mock_sidebar_radio):
    mock_sidebar_radio.return_value = "Home"
    with patch("streamlit.markdown") as mock_markdown:
        selected_page = dashboard_title()
        mock_sidebar_radio.assert_called_once_with(
            'Select a page', ['Home', 'Judgment Search', 'Analytics']
        )
        assert selected_page == "Home"
        expected_markdown = "<h2 style=\"text-align: center;\">Home Page</h2>"

        actual_markdown_call = mock_markdown.call_args[0][0].strip()
        assert actual_markdown_call == expected_markdown

@pytest.mark.parametrize("page,expected_subheader", [
    ("Home", "Home Page"),
    ("Judgment Search", "Judgment Search Page"),
    ("Analytics", "Analytics Page"),
])
def test_page_selection(page, expected_subheader):
    with patch.object(st.sidebar, "radio", return_value=page):
        with patch("streamlit.markdown") as mock_markdown:
            dashboard_title()
            expected_markdown = f"<h2 style=\"text-align: center;\">{expected_subheader}</h2>"
            actual_markdown_call = mock_markdown.call_args[0][0].strip()
            assert actual_markdown_call == expected_markdown
