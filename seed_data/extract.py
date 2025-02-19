#pylint:disable=unused-variable
"""File for functions to download judgments."""


import asyncio
import os
from datetime import datetime
import logging

import aiohttp
from bs4 import BeautifulSoup


BASE_URL = "https://caselaw.nationalarchives.gov.uk/atom.xml?per_page=9999"


async def get_judgments_from_atom_feed(url: str) -> list[dict[str, str]]:
    """Returns a list of dictionaries, each dictionary corresponding to a judgment."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as result:
                result.raise_for_status()
                soup = BeautifulSoup(await result.text(), "xml")
                entries = soup.find_all("entry")
                base_link = "https://caselaw.nationalarchives.gov.uk/"
                judgments = []
                for entry in entries:
                    link = entry.find("link", {"rel": "alternate"})["href"]
                    judgment = {
                        "title": f"{link.replace(base_link, '').replace('/', '-')}.xml",
                        "link": f"{link}/data.xml"
                    }
                    judgments.append(judgment)
                if judgments:
                    return judgments
                logging.info("No judgments found for this day.")
        except aiohttp.ClientError as e:
            logging.error("Error requesting data from URL: %s", str(e))
            raise


def create_daily_atom_feed_url(date: datetime) -> str:
    """Returns the atom feed URL of the day's judgments."""
    day, month, year = date.day, date.month, date.year
    return (f"{BASE_URL}&from_date_0={day}&from_date_1={month}"
            f"&from_date_2={year}&to_date_0={day}&to_date_1={month}&to_date_2={year}")


async def download_url(local_folder: str, url: str, file_name: str) -> None:
    """Downloads a file from a URL to a given folder asynchronously."""
    os.makedirs(local_folder, exist_ok=True)
    file_path = os.path.join(local_folder, file_name)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=60) as response:
                response.raise_for_status()
                content = await response.read()
                await asyncio.to_thread(
                    lambda: open(file_path, "wb").write(content)
                )
            logging.info("Downloaded %s to %s", url, file_path)
            await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            logging.error("Timeout error while downloading %s", url)
        except aiohttp.ClientError as e:
            logging.error("Error downloading file from URL %s: %s", url, str(e))


async def download_days_judgments(day: datetime, folder_path: str) -> None:
    """Handles getting and download judgments for a particular day."""
    daily_link = create_daily_atom_feed_url(day)
    daily_judgments = await get_judgments_from_atom_feed(daily_link)
    if daily_judgments:
        download_tasks = []
        for judgment in daily_judgments:
            download_tasks.append(download_url(folder_path, judgment["link"], judgment["title"]))

        for task in download_tasks:
            await task

        logging.info("All judgments for day %s downloaded.", day.strftime("%B %d %Y"))
