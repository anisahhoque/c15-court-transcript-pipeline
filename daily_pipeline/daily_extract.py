"""File that downloads previous day's judgments."""

from os import environ as ENV, makedirs
from datetime import datetime, timedelta
import logging

from dotenv import load_dotenv
from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://caselaw.nationalarchives.gov.uk/atom.xml?per_page=9999"


def get_judgments_from_atom_feed(url: str) -> list[dict[str, str]]:
    """Returns a list of dictionaries, each dictionary corresponding to a judgment.
    
    Each dictionary has a particular judgment's neutral citation number
    as its title (a string) and link to the judgment xml (a string)."""
    try:
        result = requests.get(url, timeout=30)
        result.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error("Error requesting data from URL: %s", str(e))
        raise
    soup = BeautifulSoup(result.text, "xml")
    entries = soup.find_all("entry")
    base_link = "https://caselaw.nationalarchives.gov.uk/"
    judgments = []
    for entry in entries:
        link = entry.find("link", {"rel": "alternate"})["href"]
        judgment = {
            "title" : f"{link.replace(base_link, "").replace("/", "-")}.xml",
            "link" : f"{link}/data.xml"
        }
        judgments.append(judgment)
    return judgments


def create_daily_atom_feed_url() -> str:
    """Returns the atom feed URL of the previous day's judgments as a string."""
    today = datetime.today() - timedelta(days = 1)
    day, month, year = today.day, today.month, today.year

    return (f"{BASE_URL}&from_date_0={day}&from_date_1={month}"
            f"&from_date_2={year}&to_date_0={day}&to_date_1={month}&to_date_2={year}")


def create_client(aws_access_key_id: str, aws_secret_access_key: str) -> BaseClient:
    """Returns a BaseClient object for s3 service specified by the provided keys"""
    try:
        s_three_client = client("s3", aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key)
        logging.info("Successfully connected to s3.")
        return s_three_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", str(e))
        raise


def upload_url_to_s3(s_three_client: BaseClient, url: str, bucket_name: str, s3_key: str) -> None:
    """Uploads a file from a URL to an S3 bucket."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        s_three_client.put_object(Bucket=bucket_name, Key=s3_key, Body=response.content)
        logging.info("File from '%s' uploaded successfully to '%s/%s'", url, bucket_name, s3_key)
    except requests.exceptions.RequestException as e:
        logging.error("Error downloading the file from URL: %s", str(e))
        raise


def download_url(local_folder: str, url: str, file_name: str) -> None:
    """Downloads file from a URL to a given folder in current path,
    creating it if it doesn't already exist."""
    makedirs(local_folder, exist_ok=True)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        file_path = f"{local_folder}/{file_name}"
        with open(file_path, "wb") as file:
            file.write(response.content)
        logging.info("XML saved to %s/%s", local_folder, file_name)
    except requests.exceptions.RequestException as e:
        logging.error("Error downloading the file from URL: %s", str(e))
        raise


# This is temporary for testing purposes
if __name__ == "__main__":
    load_dotenv()
    daily_link = create_daily_atom_feed_url()
    daily_judgments = get_judgments_from_atom_feed(daily_link)
    my_aws_access_key_id = ENV["AWS_ACCESS_KEY"]
    my_aws_secret_access_key = ENV["AWS_SECRET_ACCESS_KEY"]
    s_three = create_client(my_aws_access_key_id, my_aws_secret_access_key)
    for daily_judgment in daily_judgments:
        upload_url_to_s3(s_three, daily_judgment["link"],
                         ENV["AWS_BUCKET"], daily_judgment["title"])
        download_url("judgments", daily_judgment["link"], daily_judgment["title"])
