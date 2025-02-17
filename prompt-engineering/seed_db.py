import json
import psycopg2
import pandas as pd
from parse_xml import get_all_metadata
def combine_json(json_filenames: str) -> json:
    combined_data = []
    for filename in json_filenames:
        with open(filename+'.json', 'r', encoding='utf-8') as file:
            data = json.load(file)  
            combined_data.extend(data)  
    
    return combined_data

def seed_db(combined_data: list[dict]) -> None:

    roles = list(set([
        party['party_role'].lower()  
        for case in combined_data  
        for party in case['parties']  
    ]))

    legislations = list(set([
        legislation['legislation_name']  
        for case in combined_data  
        for argument in case['arguments']  
        for legislation in argument['legislations_referenced']  
    ]))

    counsels = list(set({
        (counsel['counsel_name'], counsel['chamber_name'])
        for case in combined_data
        for party in case['parties']
        for counsel in party['counsels']
    }))


    print(roles)
    print(legislations)
    print(counsels)
    for case in combined_data:
        judgment_type = case['type_of_crime']
        judgment_date = case['judgment_date']
        judge_name = case['judge'][0]['judge_name']
        neutral_citation = case['neutral_citation']
        judgment_summary = case['description']
        court_name = case['court_name']
        for party in case['parties']:
            party_name = party['party_name']
            party_role = party['party_role']
            for counsel in party['counsels']:
                counsel_name = counsel['counsel_name']
                chamber_name = counsel['chamber_name']
        for argument in case['arguments']:
            argument_summary = argument['summary']
            for judgment in argument['judgments_referenced']:
                neutral_citation = judgment['neutral_citation']
            for legislation in argument['legislations_referenced']:
                legislation_name = legislation['legislation_name']
                legislation_section = legislation['legislation_section']
            party_role = argument['party_role']

        in_favour_of = case['ruling']


if __name__=="__main__":
    file_names = ['ewhc_comm_2025_240.xml','ukut_iac_2021_202.xml',
                  'ewcop_t3_2025_6.xml', 'ewhc_kb_2025_287.xml',
                    'ewca-civ-2025-113.xml','ukpc_2025_7.xml']
    
    manual_json = get_all_metadata(file_names)
    gpt_json = combine_json([file.replace('.xml','.json')for file in file_names])

    combined_json = []
    

    for manual_item, gpt_item in zip(manual_json, gpt_json):
        combined_item = {**manual_item, **gpt_item}
        combined_json.append(combined_item)
    
    seed_db(combined_json)