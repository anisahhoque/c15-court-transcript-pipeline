"""Script for seeding initial database judgment data."""

from dotenv import load_dotenv
import os
from os import environ as ENV
from datetime import datetime, timedelta
from time import sleep
import logging

import requests

from extract import (create_daily_atom_feed_url, get_judgments_from_atom_feed, 
                    create_client, upload_url_to_s3, download_url)
from parse_xml import get_metadata
from prompt_engineering import get_client, get_xml_data, get_case_summary
from seed_data.load import get_db_connection, get_base_maps, seed_db_base_tables, seed_judgment_data


def list_days_between(start_date: datetime, end_date: datetime):
    """Returns a list of dates between two given dates (inclusive)."""
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]



if __name__ == "__main__":
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    api_client = get_client(ENV["API_KEY"])
    conn = get_db_connection(dbname=ENV['DB_NAME'],user=ENV['DB_USERNAME'],
                             password=ENV['DB_PASSWORD'],host=ENV['DB_HOST'],
                             port=ENV['DB_PORT'])
    my_aws_access_key_id = ENV["AWS_ACCESS_KEY"]
    my_aws_secret_access_key = ENV["AWS_SECRET_ACCESS_KEY"]
    s_three = create_client(my_aws_access_key_id, my_aws_secret_access_key)
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 31)
    for day in list_days_between(start_date, end_date):
        logging.info("------------------")
        logging.info("Day %s", day)
        logging.info("------------------")
        daily_link = create_daily_atom_feed_url(day)
        daily_judgments = get_judgments_from_atom_feed(daily_link)
        if daily_judgments:
            for daily_judgment in daily_judgments:
                try:
                    upload_url_to_s3(s_three, daily_judgment["link"],
                                    ENV["AWS_BUCKET"], daily_judgment["title"])
                    download_url("judgments", daily_judgment["link"], daily_judgment["title"])
                except requests.exceptions.RequestException as e:
                    logging.info("""Request for judgment has timed out.""")
                    continue
            judgment_data = []
            for judgment in os.listdir("judgments"):
                logger.info(f"Processing judgment {judgment}...")
                file_path = os.path.join("judgments", judgment)
                judgment_xml = get_xml_data(file_path)
                metadata = get_metadata(file_path)
                api_data = get_case_summary("gpt-4o-mini", api_client, judgment_xml)
                combined_judgment_data = metadata | api_data
                judgment_data.append(combined_judgment_data)
                os.remove(file_path)
            mappings = get_base_maps(conn)
            seed_db_base_tables(judgment_data,conn,mappings)
            updated_mappings = get_base_maps(conn)
            seed_judgment_data(conn,judgment_data,updated_mappings)
            sleep(15)

    conn.close()

        

        