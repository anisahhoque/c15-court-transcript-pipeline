"""This file extracts data from xmls using OpenAI API"""

from bs4 import BeautifulSoup

def get_metadata(xml_filename: str) -> dict:
    """Returns the meta data that can be easily extracted from the xml"""

    with open(xml_filename, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'xml')
    metadata = {
        'court_name': '',
        'neutral_citation': '',
        'judgment_date': '',
        'parties': [] 
    }

    metadata['neutral_citation'] = soup.find('neutralCitation').text if soup.find('neutralCitation') else ""
    metadata['judgment_date'] = soup.find('FRBRdate').get('date')
    court_name = soup.find("TLCOrganization")
    metadata['court_name'] = court_name.get('showAs')


    parties = soup.find_all('party')

    for party in parties:
        party_data = {
            'party_name': party.text if party.text else "",
            'party_role': party.get('as').lstrip('#'),
        }

    metadata['parties'].append(party_data)
    return metadata


if __name__=="__main__":
    print(get_metadata('ukut_iac_2021_202.xml'))
    print(get_metadata('ewca-civ-2025-113.xml'))

    #AI : judges,arguments,legislations,judgment references, counsels+chambers,
    # casenumber-doesnt always exist, hearing dates
