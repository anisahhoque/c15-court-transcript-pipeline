"""Script for seeding initial database judgment data."""


import os
from os import environ as ENV
from datetime import datetime, timedelta
import logging
import asyncio

from dotenv import load_dotenv

from daily_extract import download_days_judgments
from daily_prompt_engineering import get_client
from daily_transform import process_all_judgments
from daily_load import (get_db_connection, get_base_maps,
                  seed_db_base_tables, seed_judgment_data,
                  create_client, upload_multiple_files_to_s3)


async def main() -> None:
    """Main seeding function."""
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    api_client = get_client(ENV["OPENAI_KEY"])
    conn = get_db_connection(dbname=ENV['DB_NAME'], user=ENV['DB_USER'],
                             password=ENV['DB_PASSWORD'], host=ENV['DB_HOST'],
                             port=ENV['DB_PORT'])
    my_aws_access_key_id = ENV["ACCESS_KEY"]
    my_aws_secret_access_key = ENV["SECRET_KEY"]
    s_three = await create_client(my_aws_access_key_id, my_aws_secret_access_key)
    yesterday = datetime.today() - timedelta(days=1)
    logging.info("Judgments for Day %s", yesterday.strftime("%B %d %Y"))
    logging.info("------------------")
    await download_days_judgments("judgments")
    if os.listdir("judgments"):
        judgment_data = process_all_judgments("judgments", "judgments_html", api_client)
        mappings = get_base_maps(conn)
        seed_db_base_tables(judgment_data, conn, mappings)
        updated_mappings = get_base_maps(conn)
        seed_judgment_data(conn, judgment_data, updated_mappings)
        await upload_multiple_files_to_s3(s_three, "judgments_html", ENV["BUCKET_NAME"])
        judgment_filepaths = [os.path.join("judgments", file) for
                                file in os.listdir("judgments")]
        judgment_html_filepaths = [os.path.join("judgments_html", file) for
                                file in os.listdir("judgments_html")]
        for judgment in judgment_filepaths:
            os.remove(judgment)
        for judgment_html in judgment_html_filepaths:
            os.remove(judgment_html)


    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
