"""This file extracts data from xmls using OpenAI API"""

import logging
from bs4 import BeautifulSoup

def get_metadata(xml_filename: str) -> dict:
    """Returns the meta data that can be easily extracted from the xml"""

    try:
        with open(xml_filename, 'r', encoding='UTF-8') as file:
            soup = BeautifulSoup(file, 'xml')
    except FileNotFoundError:
        logging.error('File was not found - %s', xml_filename)
    except Exception:
        logging.error('Invalid xml content - %s', xml_filename)
    metadata = {
        'court_name': '',
        'neutral_citation': '',
        'judgment_date': ''}

    neutral_citation = soup.find('neutralCitation')
    metadata['neutral_citation'] = neutral_citation.text if soup.find('neutralCitation') and neutral_citation.text else None

    date = soup.find('FRBRdate')
    metadata['judgment_date'] = date.get('date') if date and date.get('date') else None

    court_name = soup.find('TLCOrganization')
    metadata['court_name'] = court_name.get('showAs') if court_name and court_name.get('showAs') else None

    return metadata

def get_all_metadata(xml_filenames: str) -> list[dict]:
    """Returns a list of dictionaries with the extracted metadata"""
    return [get_metadata(filename) for filename in xml_filenames]

if __name__=="__main__":
    
    print(get_metadata('ukut_iac_2021_202.xml'))
    print(get_metadata('ewca-civ-2025-113.xml'))
