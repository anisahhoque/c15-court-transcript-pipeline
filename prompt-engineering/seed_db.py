"""Seeding initial judgment data."""

from os import environ as ENV

import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor, execute_values
import pandas as pd
from parse_xml import get_all_metadata

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


def get_connection():
    return psycopg2.connect(
                dbname="judgments",  
                user="rina",   
                host="localhost",  
                port="5432"  
                )

def combine_json(json_filenames: str) -> json:
    combined_data = []
    for filename in json_filenames:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)  
            combined_data.extend(data)  
    
    return combined_data


def seed_base_tables(conn: connection, judgment_data: list[dict]) -> None:
    """Seed judgment data after AI processing.
    Returns none."""
    unique_judgment_types = ["criminal, civil"]
    unique_courts = tuple(set([judgment["court_name"].lower() for judgment in judgment_data]))
    unique_roles = tuple(set([party["party_role"].lower() for judgment in judgment_data for party in judgment["parties"]]))
    unique_counsels = tuple(set(counsel["counsel_name"].lower()
                                        for judgment in judgment_data
                                        for party in judgment["parties"]
                                        for counsel in party["counsels"]))
    unique_chambers = tuple(set([counsel["chamber_name"].lower()
                                        for judgment in judgment_data
                                        for party in judgment["parties"]
                                        for counsel in party["counsels"]]))
    
    with conn.cursor() as cursor:
        cursor.execute_values("""INSERT INTO court
        VALUES (%s)
        RETURNING court_name, court_id""", unique_courts)
        court_map = {x["court_name"]: x["court_id"] for x in cursor.fetchall()}
        cursor.execute_values("""INSERT INTO role
        VALUES (%s)
        RETURNING role_name, role_id""", unique_roles)
        role_map = {x["role_name"]: x["role_id"] for x in cursor.fetchall()}
        cursor.execute("""INSERT INTO judgment_type
        VALUES (%s)
        RETURNING judgment_type, judgment_type_id""", unique_judgment_types)
        judgment_type_map = {x["judgment_type"]: x["judgment_type_id"] for x in cursor.fetchall()}
        cursor.execute("""INSERT INTO counsel
        VALUES (%s)
        RETURNING counsel_name, counsel_id""", unique_counsels)
        counsel_map = {x["counsel_name"]: x["counsel_id"] for x in cursor.fetchall()}
        cursor.execute("""INSERT INTO chamber
        VALUES (%s)
        RETURNING chamber_name, chamber_id""", unique_chambers)
        chamber_map = {x["chamber_name"]: x["chamber_id"] for x in cursor.fetchall()}


def seed_db(combined_data: list[dict], conn) -> None:
    cursor = conn.cursor()
    roles = set([
        party['party_role'].lower()
        for case in combined_data  
        for party in case['parties']  
    ])

    role_insert_query = """insert into role (role_name) values (%s) returning role_id, role_name"""
    cursor.executemany(role_insert_query,[(role,)for role in roles])
    role_mapping = cursor.fetchall()
    print(role_mapping)

    counsels = set([
        counsel['counsel_name']
        for case in combined_data
        for party in case['parties']
        for counsel in party['counsels']
    ])

    counsels_insert_query = """insert into counsel (counsel_name) values (%s)"""
    cursor.executemany(counsels_insert_query, [(counsel,) for counsel in counsels])
    courts = set([
        (case['court_name'])
        for case in combined_data
    ])

    court_insert_query = """insert into court (court_name) values (%s)"""
    cursor.executemany(court_insert_query, [(court,) for court in courts])

    chambers = set([
        (counsel['chamber_name'])
        for case in combined_data
        for party in case['parties']
        for counsel in party['counsels']
    ])

    chambers_insert_query = """insert into chamber (chamber_name) values (%s)"""
    cursor.executemany(chambers_insert_query, [(chamber,) for chamber in chambers])

    cursor.close()

    for case in combined_data:
        judgment_type = case['type_of_crime']
        judgment_date = case['judgment_date']
        judge_name = case['judge']
        neutral_citation = case['neutral_citation']
        judgment_summary = case['description']
        court_name = case['court_name']
        for party in case['parties']:
            party_name = party['party_name']
            party_role = party['party_role']
            for counsel in party['counsels']:
                counsel_name = counsel['counsel_name']
                chamber_name = counsel['chamber_name']


        in_favour_of = case['ruling']
    conn.commit()

if __name__=="__main__":
    conn = get_connection()
    file_names = ['ewhc_comm_2025_240.xml','ukut_iac_2021_202.xml',
                  'ewcop_t3_2025_6.xml', 'ewhc_kb_2025_287.xml',
                    'ewca-civ-2025-113.xml','ukpc_2025_7.xml']
    
    manual_json = get_all_metadata(file_names)
    gpt_json = combine_json([file.replace('.xml','.json')for file in file_names])

    combined_json = []
    

    for manual_item, gpt_item in zip(manual_json, gpt_json):
        combined_item = {**manual_item, **gpt_item}
        combined_json.append(combined_item)
    
    seed_db(combined_json,conn)
    conn.close()