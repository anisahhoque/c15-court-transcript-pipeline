import asyncio
from aioresponses import aioresponses
import aiofiles
import pytest
from unittest.mock import patch, AsyncMock, call
from datetime import datetime
from extract import (
    get_judgments_from_atom_feed,
    create_daily_atom_feed_url,
    download_url,
    download_days_judgments,
)
def generate_test_cases():
    base_url = "https://caselaw.nationalarchives.gov.uk/atom.xml?per_page=9999"
    dates = [
        datetime(2023, 10, 1),
        datetime(2020, 1, 15),
        datetime(2022, 7, 4),
        datetime(2021, 3, 10),
        datetime(2024, 2, 29), 
        datetime(2019, 12, 31),
        datetime(2018, 1, 1),
        datetime(2022, 6, 15),
        datetime(2023, 9, 23),
        datetime(2025, 5, 19),
        datetime(2026, 11, 11),
        datetime(2024, 8, 21),
        datetime(2030, 7, 17),
        datetime(2017, 2, 28),
        datetime(2016, 2, 29),
        datetime(2021, 6, 30),
        datetime(2029, 12, 24),
        datetime(2013, 10, 31),
        datetime(2001, 5, 25),
        datetime(1999, 12, 31)
    ]

    return [
        (
            date,
            (
                f"{base_url}&from_date_0={date.day}&from_date_1={date.month}&from_date_2={date.year}"
                f"&to_date_0={date.day}&to_date_1={date.month}&to_date_2={date.year}"
            ),
        )
        for date in dates
    ]

@pytest.mark.parametrize("date, expected_url", generate_test_cases())
def test_create_daily_atom_feed_url(date, expected_url):
    """Test the creation of the daily atom feed url."""
    result = create_daily_atom_feed_url(date)
    assert result == expected_url


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
    # Prepare the mocked HTTP response
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
    """Test downloading all judgments in a day."""
    mock_get_judgments = mocker.patch(
        "extract.get_judgments_from_atom_feed",
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

    mock_download_url = mocker.patch("extract.download_url", new_callable=AsyncMock)

    date = datetime(2023, 10, 1)
    folder_path = "judgments"
    await download_days_judgments(date, folder_path)

    mock_get_judgments.assert_called_once_with(
        "https://caselaw.nationalarchives.gov.uk/atom.xml?per_page=9999&from_date_0=1&from_date_1=10&from_date_2=2023&to_date_0=1&to_date_1=10&to_date_2=2023"
    )

    mock_download_url.assert_has_calls(
        [
            call("judgments", "https://mock-link.com/judgment1/data.xml", "judgment1.xml"),
            call("judgments", "https://mock-link.com/judgment2/data.xml", "judgment2.xml"),
        ],
        any_order=False
    )

