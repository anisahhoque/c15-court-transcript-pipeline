"""Script for seeding initial database judgment data."""

from dotenv import load_dotenv
import os
from os import environ as ENV
from datetime import datetime, timedelta
import logging
import asyncio

from extract_asyncio import download_days_judgments
from parse_xml import get_metadata
from prompt_engineering import get_client, get_xml_data, get_case_summary
from load import get_db_connection, get_base_maps, seed_db_base_tables, seed_judgment_data, create_client, upload_multiple_files_to_s3


def list_days_between(start_date: datetime, end_date: datetime):
    """Returns a list of dates between two given dates (inclusive)."""
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


async def main() -> None:
    """Main seeding function."""
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    api_client = get_client(ENV["API_KEY"])
    conn = get_db_connection(dbname=ENV['DB_NAME'], user=ENV['DB_USERNAME'],
                             password=ENV['DB_PASSWORD'], host=ENV['DB_HOST'],
                             port=ENV['DB_PORT'])
    my_aws_access_key_id = ENV["AWS_ACCESS_KEY"]
    my_aws_secret_access_key = ENV["AWS_SECRET_ACCESS_KEY"]
    s_three = await create_client(my_aws_access_key_id, my_aws_secret_access_key)
    start_date = datetime(2025, 1, 2)
    end_date = datetime(2025, 1, 3)
    for day in list_days_between(start_date, end_date):
        logging.info("------------------")
        logging.info("Day %s", day)
        logging.info("------------------")
        await download_days_judgments(day, "judgments")
        judgment_data = []
        judgment_filepaths = [os.path.join("judgments", file) for file in os.listdir("judgments")]
        judgment_files = os.listdir("judgments")
        for judgment in judgment_files:
            logger.info(f"Processing judgment {judgment}...")
            file_path = os.path.join("judgments", judgment)
            judgment_xml = get_xml_data(file_path)
            metadata = get_metadata(file_path)
            api_data = get_case_summary("gpt-4o-mini", api_client, judgment_xml)
            combined_judgment_data = metadata | api_data
            judgment_data.append(combined_judgment_data)
        mappings = get_base_maps(conn)
        seed_db_base_tables(judgment_data, conn, mappings)
        updated_mappings = get_base_maps(conn)
        seed_judgment_data(conn, judgment_data, updated_mappings)
        await upload_multiple_files_to_s3(s_three, judgment_filepaths, ENV["AWS_BUCKET"])
        for judgment in judgment_filepaths:
            os.remove(judgment)
        await asyncio.sleep(15)  

    conn.close()  


if __name__ == "__main__":
    asyncio.run(main())

        

        