from aioresponses import aioresponses
import aiofiles
import pytest
from unittest.mock import AsyncMock, call
from datetime import datetime, timedelta
from daily_extract import (
    get_judgments_from_atom_feed,
    create_daily_atom_feed_url,
    download_url,
    download_days_judgments,
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
    assert create_daily_atom_feed_url() == expected_url


@pytest.mark.asyncio
async def test_get_judgments_from_atom_feed():
    """Test get_judgments_from_atom_feed with mocked HTTP response."""
    mock_response = """
    <feed>
        <entry>
            <link rel="alternate" href="https://caselaw.nationalarchives.gov.uk/id1"/>
        </entry>
        <entry>
            <link rel="alternate" href="https://caselaw.nationalarchives.gov.uk/id2"/>
        </entry>
    </feed>
    """
    
    with aioresponses() as mock_server:
        mock_server.get("https://fake-url.com", status=200, body=mock_response)
        
        result = await get_judgments_from_atom_feed("https://fake-url.com")
        assert len(result) == 2
        assert result[0]["title"] == "id1.xml"
        assert result[0]["link"] == "https://caselaw.nationalarchives.gov.uk/id1/data.xml"
        assert result[1]["title"] == "id2.xml"
        assert result[1]["link"] == "https://caselaw.nationalarchives.gov.uk/id2/data.xml"


@pytest.mark.asyncio
async def test_download_url(tmp_path):
    """Test download_url with mocked HTTP response."""
    mock_file_content = b"dummy content"
    with aioresponses() as mock_server:
        mock_server.get("<https://fake-url.com/data.xml>", status=200, body=mock_file_content)
        
        local_folder = tmp_path / "judgments"
        local_folder.mkdir()
        
        await download_url(str(local_folder), "<https://fake-url.com/data.xml>", "test_file.xml")

        file_path = local_folder / "test_file.xml"
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()
        assert file_content == mock_file_content


@pytest.mark.asyncio
async def test_download_days_judgments(mocker):
    """Test downloading all of yesterday's judgments."""
    mock_get_judgments = mocker.patch(
        "daily_extract.get_judgments_from_atom_feed",
        new_callable=AsyncMock,
        return_value=[
            {
                "title": "judgment1.xml",
                "link": "https://mock-link.com/judgment1/data.xml",
            },
            {
                "title": "judgment2.xml",
                "link": "https://mock-link.com/judgment2/data.xml",
            },
        ],
    )

    mock_download_url = mocker.patch("daily_extract.download_url", new_callable=AsyncMock)

    folder_path = "judgments"
    await download_days_judgments(folder_path)

    yesterday = datetime.today() - timedelta(days=1)
    expected_url = (
        f"{BASE_URL}&from_date_0={yesterday.day}&from_date_1={yesterday.month}"
        f"&from_date_2={yesterday.year}&to_date_0={yesterday.day}"
        f"&to_date_1={yesterday.month}&to_date_2={yesterday.year}"
    )

    mock_get_judgments.assert_called_once_with(
        expected_url
    )

    mock_download_url.assert_has_calls(
        [
            call("judgments", "https://mock-link.com/judgment1/data.xml", "judgment1.xml"),
            call("judgments", "https://mock-link.com/judgment2/data.xml", "judgment2.xml"),
        ],
        any_order=False
    )

