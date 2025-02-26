import re
import pytest
from unittest.mock import patch, call
from components import dashboard_title, homepage_text


def test_dashboard_title():
    """Test if dashboard_title calls st.markdown with the correct argument."""
    with patch("streamlit.html") as mock_markdown:
        dashboard_title()
        args, kwargs = mock_markdown.call_args
        assert args[0].strip() == """
        <header style="text-align: center; font-size: 60px;">Judgment Reader</header>
        """.strip()



def normalize_whitespace(text):
    """Remove excessive whitespace and normalize indentation."""
    return re.sub(r'\s+', ' ', text.strip())


def test_homepage_text():
    """Test if homepage_text calls st.markdown correctly."""
    with patch("streamlit.html") as mock_markdown:
        homepage_text()

        assert mock_markdown.call_count == 1

        actual_call = mock_markdown.call_args[0][0]

        expected_html = """
            <p style="text-align: center">
            Welcome to the Court Transcript Pipeline.</p>
        """

        assert normalize_whitespace(
            actual_call) == normalize_whitespace(expected_html)
