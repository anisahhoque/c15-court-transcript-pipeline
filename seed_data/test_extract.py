# pylint: disable=unused-argument
"""Test file for extract.py"""

import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from extract import (
    get_judgments_from_atom_feed,
    create_daily_atom_feed_url,
    upload_url_to_s3,
    download_url,
    create_client,
)

BASE_URL = "https://caselaw.nationalarchives.gov.uk/atom.xml?per_page=9999"

def test_create_daily_atom_feed_url():
    """Tests that function returns the expected url."""
    yesterday = datetime.today() - timedelta(days=1)
    expected_url = (
        f"{BASE_URL}&from_date_0={yesterday.day}&from_date_1={yesterday.month}"
        f"&from_date_2={yesterday.year}&to_date_0={yesterday.day}"
        f"&to_date_1={yesterday.month}&to_date_2={yesterday.year}"
    )
    assert create_daily_atom_feed_url(yesterday) == expected_url

@pytest.fixture(name="mock_requests_get")
def fixture_mock_requests_get(mocker):
    """Fixture for patching requests.get."""
    return mocker.patch("requests.get")

def test_get_judgments_from_atom_feed(mock_requests_get):
    """Tests that the function returns a list of dicts of appropriate values."""
    mock_response = MagicMock()
    mock_response.text = """
    <feed>
        <entry>
            <title>Test judgment</title>
            <link rel="alternate" href="https://caselaw.nationalarchives.gov.uk/ewca/civ/2025/108" />
        </entry>
    </feed>
    """
    mock_requests_get.return_value = mock_response
    mock_requests_get.return_value.raise_for_status = MagicMock()
    expected = [{
        "title": "ewca-civ-2025-108.xml",
        "link": "https://caselaw.nationalarchives.gov.uk/ewca/civ/2025/108/data.xml"
    }]
    assert get_judgments_from_atom_feed("dummy_url") == expected
    mock_requests_get.assert_called_once_with("dummy_url", timeout=30)


def test_get_judgments_from_atom_feed_logging(mock_requests_get, caplog):
    """Tests when the function raises a requestexception, including its log message."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = \
        requests.exceptions.RequestException("Request failed")
    mock_requests_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.exceptions.RequestException):
            get_judgments_from_atom_feed("dummy_url")
    assert "Error requesting data from URL:" in caplog.text


parameters = [
        ("https://example.com/file1.xml", "file1.xml", b"file1 content"),
        ("https://example.com/file2.json", "file2.json", b"file2 content"),
        ("https://example.com/file3.csv", "file3.csv", b"file3 content"),
        ("https://example.com/file4.txt", "file4.txt", b"file4 content"),
        ("https://example.com/file5.html", "file5.html", b"file5 content"),
    ]

@pytest.mark.parametrize(
    "url, filename, content",
    parameters,
)
def test_upload_url_to_s3(mock_requests_get, url, filename, content):
    """Tests that the upload_url_to_s3 function correctly fetches and uploads files."""
    mock_s3_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = content
    mock_requests_get.return_value = mock_response
    mock_requests_get.return_value.raise_for_status = MagicMock()

    upload_url_to_s3(mock_s3_client, url, "test-bucket", filename)

    mock_requests_get.assert_called_once_with(url, timeout=30)
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket", Key=filename, Body=content
    )


def test_upload_url_to_s3_logging(mock_requests_get, caplog):
    """Tests when the function raises a requestexception, including its log message."""
    mock_s3_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = \
        requests.exceptions.RequestException("Download failed")
    mock_requests_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.exceptions.RequestException):
            upload_url_to_s3(mock_s3_client, "https://example.com/file.xml",
                             "test-bucket", "folder/file.xml")
    assert "Error downloading the file from URL:" in caplog.text


@pytest.mark.parametrize(
    "url, filename, content",
    parameters,
)
def test_download_url(tmp_path, mock_requests_get, url, filename, content):
    """Tests that the download_url function correctly fetches and saves files."""
    mock_response = MagicMock()
    mock_response.content = content
    mock_requests_get.return_value = mock_response
    mock_requests_get.return_value.raise_for_status = MagicMock()
    download_url(tmp_path, url, filename)
    file_path = tmp_path / filename
    with open(file_path, "rb") as f:
        assert f.read() == content
    mock_requests_get.assert_called_once_with(url, timeout=30)


def test_download_url_logging(tmp_path, mock_requests_get, caplog):
    """Tests when the function raises a requestexception, including its log message."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = \
        requests.exceptions.RequestException("Download failed")
    mock_requests_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.exceptions.RequestException):
            download_url(tmp_path, "https://example.com/file.xml", "file.xml")
    assert "Error downloading the file from URL:" in caplog.text


@patch("extract.client")
def test_create_client(mock_boto_client):
    """Tests the create client function calls the appropriate function with the 
     correct parameters."""
    mock_env = {
        "AWS_ACCESS_KEY": "test-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret"
    }
    create_client(mock_env["AWS_ACCESS_KEY"], mock_env["AWS_SECRET_ACCESS_KEY"])
    mock_boto_client.assert_called_once_with(
        "s3", aws_access_key_id="test-key", aws_secret_access_key="test-secret"
    )


@patch("extract.client", side_effect=NoCredentialsError)
def test_create_client_no_credentials(mock_boto_client, caplog):
    """Tests when there is no credentials when attempting to connect to s3."""
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoCredentialsError):
            create_client("wrong", "wrong")
    assert "Credentials error:" in caplog.text


@patch("extract.client", side_effect=PartialCredentialsError(provider="aws", cred_var="test"))
def test_create_env_client_partial_credentials(mock_boto_client, caplog):
    """Tests when there is partial credentials when attempting to connect to s3."""
    with caplog.at_level(logging.ERROR):
        with pytest.raises(PartialCredentialsError):
            create_client("right", "wrong")
    assert "Credentials error:" in caplog.text
