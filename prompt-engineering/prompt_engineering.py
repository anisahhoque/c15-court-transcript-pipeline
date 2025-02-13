"""This file extracts data from xmls using OpenAI API"""
import re
from bs4 import BeautifulSoup



def get_metadata(xml_filename: str) -> dict:
    """Returns the meta data that can be easily extracted from the xml"""

    with open(xml_filename, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'xml')
    metadata = {
        'court_name': '',
        'case_number': '',
        'neutral_citation': '',
        'judgment_date': '',
        'hearing_date': '',
        'judge': [],
        'parties': [] 
    }

    metadata['neutral_citation'] = soup.find('neutralCitation').text if soup.find('neutralCitation') else ""
    judges = soup.find_all('TLCPerson')
    for x in judges:
        print(x.get('showAs'))
    metadata['case_number'] = soup.find('docketNumber').text if soup.find('docketNumber') else ""
    metadata['judgment_date'] = soup.find('FRBRdate').get('date')

    court_name = soup.find("TLCOrganization")
    metadata['court_name'] = court_name.get('showAs')


    parties = soup.find_all('party')

    p_tags = soup.find_all('p', style="text-align:center")
    for party in parties:
        party_data = {
            'party_name': party.text if party.text else "",
            'party_role': party.get('as'),
            'counsels': []
        }

        for p_tag in p_tags:
            if 'hearing date' in p_tag.text.lower():
                match = re.search(r'\b\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}\b', p_tag.text)
                if match:
                    hearing_date = match.group()
                    metadata['hearing_date'] = hearing_date


            contain_span = p_tag.find_all('span')
            for span in contain_span:
                if party.text.strip().lower() in span.text.strip().lower():
                    counsel_text = ' '.join([span.text.strip() for span in contain_span])
                    chamber_match = re.search(r'\(instructed by ([^)]+)\)', counsel_text)
                    chamber = chamber_match.group(1) if chamber_match else "Unknown"
                    counsel_names = counsel_text[:counsel_text.find('(')].split('and')
                    for name in counsel_names:
                        counsel = {}
                        counsel['counsel_name'] = name.strip()
                        counsel['chamber_name'] = chamber
                        party_data['counsels'].append(counsel)
            



  
        metadata['parties'].append(party_data)

    

    #print(metadata)
if __name__=="__main__":
    get_metadata('ukut_iac_2021_202.xml')
    #get_metadata('ewca-civ-2025-113.xml')

    #Confident in retrieving: court name, neutral citation, judgement date, parties+roles
    #Could retrieve: case number - didnt always exist, hearing date
    #AI : judges,arguments,legislations,judgment references, counsels+chambers
