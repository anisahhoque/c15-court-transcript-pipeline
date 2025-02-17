"""Seeding initial judgment data."""

from os import environ as ENV
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor, execute_values
import pandas as pd
from parse_xml import get_all_metadata

load_dotenv()

def get_db_connection(dbname: str, user: str, password: str, host: str, port: str) -> connection:
    """Establishes a connection to PostgreSQL.
    Returns a PostgreSQL connection object."""
    try:
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port,
            cursor_factory=RealDictCursor)
        return conn
    except psycopg2.DatabaseError as e:
        raise psycopg2.DatabaseError(f"Error connecting to database.") from e


def combine_json(json_filenames: str) -> json:
    """Combine all jsons produced from the AI into one json"""
    combined_data = []
    for filename in json_filenames:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)  
            combined_data.extend(data)  
    
    return combined_data


def seed_db_base_tables(combined_data: list[dict], conn: connection) -> dict[dict]:
    """Seeds all the base tables, returning """
    cursor = conn.cursor()
    roles = set([
        party['party_role'].lower()
        for case in combined_data  
        for party in case['parties']  
    ])
    print(roles)
    roles = [(role,) for role in roles]
    role_insert_query = """insert into role (role_name) values %s returning role_id, role_name"""
    execute_values(cursor, role_insert_query, roles)
    role_mapping = {x["role_name"]: x["role_id"] for x in cursor.fetchall()}


    courts = set([
        (case['court_name'])
        for case in combined_data
    ])
    courts = [(court,) for court in courts]
    court_insert_query = """insert into court (court_name) values %s returning court_id, court_name"""
    execute_values(cursor, court_insert_query, courts)
    court_mapping = {x["court_name"]: x["court_id"] for x in cursor.fetchall()}

    chambers = set([
        (counsel['chamber_name'])
        for case in combined_data
        for party in case['parties']
        for counsel in party['counsels']
    ])
    chambers = [(chamber,) for chamber in chambers]
    chambers_insert_query = """insert into chamber (chamber_name) values %s returning chamber_id, chamber_name"""
    execute_values(cursor, chambers_insert_query, chambers)
    chamber_mapping = {x["chamber_name"]: x["chamber_id"] for x in cursor.fetchall()}

    judgement_type_query = """select judgment_type_id, judgment_type from judgment_type"""
    cursor.execute(judgement_type_query)
    judgment_type_mapping = {x["judgment_type"]: x["judgment_type_id"] for x in cursor.fetchall()}
    cursor.close()
    conn.commit()
    return {
        "role_map" : role_mapping,
        "chamber_map" : chamber_mapping,
        "court_map" : court_mapping,
        "judgment_type_map": judgment_type_mapping
        }


def seed_judgment_data(conn: connection, combined_data: list[dict],
                       base_maps: dict[dict, dict, dict, dict]) -> None:
    """Seeds judgment data into database.
    Returns None."""


    role_map = base_maps["role_map"]
    chamber_map = base_maps["chamber_map"]
    court_map = base_maps["court_map"]
    judgment_type_map = base_maps["judgment_type_map"]

    judgment_table_data = []
    party_table_data = []
    counsel_table_data = []
    counsel_assignment_table_data = []
    
    for case in combined_data:
   
   
        in_favour_of = case['ruling']
        judgment_type = case['type_of_crime'].lower()
        judgment_date = case['judgment_date']
        judge_name = case['judge']
        neutral_citation = case['neutral_citation']
        judgment_summary = case['judgment_description']
        court_name = case['court_name']
        for party in case['parties']:
            party_name = party['party_name']
            party_role = party['party_role'].lower()
            party_table_data.append((party_name,
                                     role_map[party_role],
                                     neutral_citation))
            for counsel in party['counsels']:
                chamber_id = chamber_map[counsel['chamber_name']]
                counsel_name = counsel['counsel_name']
                counsel_table_data.append((counsel_name, chamber_id))

        judgment_table_data.append((neutral_citation,
                                    court_map[court_name],
                                    judgment_date,
                                    judgment_summary,
                                    in_favour_of,
                                    judgment_type_map[judgment_type],
                                    judge_name))
        
        print(judgment_table_data)
    
        with conn.cursor() as cursor:

            judgment_table_insert_query = """insert into judgment
            values %s"""
            execute_values(cursor, judgment_table_insert_query,
                           judgment_table_data[-1])
            conn.commit()
            party_table_insert_query = """insert into party
            values %s returning party_name, party_id"""
            execute_values(cursor, party_table_insert_query,
                           party_table_data)
            conn.commit()
            party_map = {x["party_name"]: x["party_id"] for x in cursor.fetchall()}
            counsel_table_insert_query = """insert into counsel
            values %s returning counsel_name, counsel_id"""
            execute_values(cursor, counsel_table_insert_query, counsel_table_data)
            conn.commit()
            counsel_map = {x["counsel_name"]: x["counsel_id"] for x in cursor.fetchall()}

        for party in case['parties']:
            party_id = party_map[party['party_name']]
            for counsel in party['counsels']:
                counsel_id = counsel_map[counsel['counsel_name']]
                counsel_assignment_table_data.append(party_id, counsel_id)

        with conn.cursor() as cursor:
            counsel_assignment_insert_query = """insert into counsel_assignment
            values %s"""
            execute_values(cursor, counsel_assignment_insert_query,
                           counsel_assignment_table_data)
            conn.commit()



if __name__=="__main__":
    conn = get_db_connection(dbname=ENV['DB_NAME'],user=ENV['USER'],password='',host=ENV['HOST'],port=ENV['PORT'])
    file_names = ['ewhc_comm_2025_240.xml','ukut_iac_2021_202.xml',
                  'ewcop_t3_2025_6.xml', 'ewhc_kb_2025_287.xml',
                    'ewca-civ-2025-113.xml','ukpc_2025_7.xml']
    
    manual_json = get_all_metadata(file_names)
    gpt_json = combine_json([file.replace('.xml','.json')for file in file_names])

    combined_json = []
    

    for manual_item, gpt_item in zip(manual_json, gpt_json):
        combined_item = {**manual_item, **gpt_item}
        combined_json.append(combined_item)
    
    mappings = seed_db_base_tables(combined_json,conn)
    seed_judgment_data(conn,combined_json,mappings )

    conn.close()