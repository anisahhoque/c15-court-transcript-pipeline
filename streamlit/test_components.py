from unittest.mock import patch
import components  # Ensure your `components.py` is correctly imported
import re
import components  # Ensure this imports your components module
import pytest
from unittest.mock import patch, call
import components


def test_dashboard_title():
    """Test if dashboard_title calls st.markdown with the correct argument."""
    with patch("streamlit.html") as mock_markdown:
        components.dashboard_title()
        # Normalize whitespace before comparison
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
        components.homepage_text()

        # Ensure one markdown call was made
        assert mock_markdown.call_count == 1

        # Extract actual call arguments
        actual_call = mock_markdown.call_args[0][0]  # Extract first argument

        # Expected HTML (normalized)
        expected_html = """
            <p style="text-align: center">
            Welcome to the Court Transcript Pipeline.</p>
        """

        # Compare normalized versions
        assert normalize_whitespace(
            actual_call) == normalize_whitespace(expected_html)
