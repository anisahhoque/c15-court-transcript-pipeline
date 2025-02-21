"""Transforming judgment xml to data ready to upload to database."""
import os
import logging

from openai import OpenAI

from daily_parse_xml import get_metadata, convert_judgment
from daily_prompt_engineering import get_xml_data, get_case_summary

def process_all_judgments(folder_path: str, html_folder_path: str, api_client: OpenAI) -> list[dict]:
    """Process judgment data, extracting relevant information and returning a list of dicts."""
    judgment_data = []
    judgment_files = os.listdir(folder_path)
    logging.info("Processing judgments...")
    for judgment in judgment_files:
        file_path = os.path.join(folder_path, judgment)
        convert_judgment(html_folder_path, file_path, judgment)
        judgment_xml = get_xml_data(file_path)
        metadata = get_metadata(file_path)
        api_data = get_case_summary("gpt-4o-mini", api_client, judgment_xml)
        combined_judgment_data = metadata | api_data
        judgment_data.append(combined_judgment_data)
    logging.info("Successfully processed judgments.")
    return judgment_data
