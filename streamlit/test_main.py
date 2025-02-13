"""Tests main.py"""
import pytest
from unittest.mock import patch
from main import main


@patch("main.dashboard_title")
def test_main(mock_dashboard_title):
    main()
    mock_dashboard_title.assert_called_once()