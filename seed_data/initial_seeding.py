"""Script for seeding initial database judgment data."""

from dotenv import load_dotenv
import os
from os import environ as ENV
from datetime import datetime, timedelta
import logging
import asyncio

from extract import download_days_judgments
from prompt_engineering import get_client
from transform import process_all_judgments
from load import get_db_connection, get_base_maps, seed_db_base_tables, seed_judgment_data, create_client, upload_multiple_files_to_s3


def list_days_between(start_date: datetime, end_date: datetime):
    """Returns a list of dates between two given dates (inclusive)."""
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


async def main() -> None:
    """Main seeding function."""
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    api_client = get_client(ENV["OPENAI_KEY"])
    conn = get_db_connection(dbname=ENV['DB_NAME'], user=ENV['DB_USERNAME'],
                             password=ENV['DB_PASSWORD'], host=ENV['DB_HOST'],
                             port=ENV['DB_PORT'])
    my_aws_access_key_id = ENV["AWS_ACCESS_KEY"]
    my_aws_secret_access_key = ENV["AWS_SECRET_ACCESS_KEY"]
    s_three = await create_client(my_aws_access_key_id, my_aws_secret_access_key)
    start_date = datetime(2025, 1, 1)
    end_date = datetime.today()
    for day in list_days_between(start_date, end_date):
        logging.info("Day %s", day)
        logging.info("------------------")
        await download_days_judgments(day, "judgments")
        judgment_data = process_all_judgments("judgments", api_client)
        mappings = get_base_maps(conn)
        seed_db_base_tables(judgment_data, conn, mappings)
        updated_mappings = get_base_maps(conn)
        seed_judgment_data(conn, judgment_data, updated_mappings)
        await upload_multiple_files_to_s3(s_three, "judgments", ENV["AWS_BUCKET"])
        judgment_filepaths = [os.path.join("judgments", file) for file in os.listdir("judgments")]
        for judgment in judgment_filepaths:
            os.remove(judgment)
        await asyncio.sleep(15)  

    conn.close()  


if __name__ == "__main__":
    asyncio.run(main())

        

        