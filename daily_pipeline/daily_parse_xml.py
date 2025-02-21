"""Functions to extract metadata from XML and convert to html"""
import logging
import os

from bs4 import BeautifulSoup


def get_metadata(xml_filename: str) -> dict:
    """Returns the meta data that can be easily extracted from the xml"""

    try:
        with open(xml_filename, 'r', encoding='UTF-8') as file:
            soup = BeautifulSoup(file, 'xml')
    except FileNotFoundError:
        logging.error('File was not found - %s', xml_filename)
    metadata = {
        'court_name': '',
        'neutral_citation': '',
        'judgment_date': ''}

    neutral_citation = soup.find('neutralCitation')
    metadata['neutral_citation'] = neutral_citation.text if \
        soup.find('neutralCitation') and neutral_citation.text else None

    date = soup.find('FRBRdate')
    metadata['judgment_date'] = date.get('date') if date and date.get('date') else None

    court_name = soup.find('TLCOrganization')
    metadata['court_name'] = court_name.get('showAs') if \
        court_name and court_name.get('showAs') else None

    return metadata


def convert_judgment(html_folder_path: str, xml_file_path: str, xml_file_name: str) -> None:
    """Converts the judgment xml to html and then saved, returns None."""
    os.makedirs(html_folder_path, exist_ok=True)
    try:
        with open(xml_file_path, 'r', encoding='UTF-8') as file:
            soup = BeautifulSoup(file, 'xml')
    except FileNotFoundError:
        logging.error('File was not found - %s', xml_file_path)

    judgment_html = soup.find('judgmentBody')
    if judgment_html:
        html_file_path = os.path.join(html_folder_path,
                                      xml_file_name.replace('xml', 'html'))
        with open(html_file_path, 'w', encoding='UTF-8') as file:
            file.write(str(judgment_html))
    else:
        logging.error("No judgmentBody found in the XML.")
