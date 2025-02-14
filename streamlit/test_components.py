import pytest
from unittest.mock import patch, call
import components


def test_dashboard_title():
    """Test if dashboard_title calls st.title with the correct argument."""
    with patch("streamlit.title") as mock_title:
        components.dashboard_title()
        mock_title.assert_called_once_with("Judgment Reader")


def test_homepage_text():
    """Test if homepage_text calls st.markdown correctly."""
    with patch("streamlit.markdown") as mock_markdown:
        components.homepage_text()

        # Ensure two markdown calls were made
        assert mock_markdown.call_count == 2

        # Expected calls (ignore whitespace issues)
        expected_calls = [
            call("<h2 style=\"text-align: center;\">Home</h2>",
                 unsafe_allow_html=True),
            # Just checking it was called
            call("<p style=\"text-align: center;\">", unsafe_allow_html=True)
        ]

        for expected in expected_calls:
            assert any(expected[0] in call[0][0]
                       for call in mock_markdown.call_args_list)
