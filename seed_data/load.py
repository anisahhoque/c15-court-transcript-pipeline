"""Seeding initial judgment data."""
import os
import logging
import asyncio

import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor, execute_values
from botocore.exceptions import BotoCoreError
from boto3 import client
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_db_connection(dbname: str, user: str, password: str, host: str, port: str) -> connection:
    """Establishes a connection to PostgreSQL.
    Returns a PostgreSQL connection object."""
    try:
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port,
            cursor_factory=RealDictCursor)
        return conn
    except psycopg2.DatabaseError as e:
        raise psycopg2.DatabaseError("Error connecting to database.") from e


def get_judgment_type_mapping(conn: connection) -> dict:
    """Gets map of existing judgment types from database.
    Returns a dictionary."""
    with conn.cursor() as cursor:
        cursor.execute("""select judgment_type, judgment_type_id from judgment_type""")
        return {x["judgment_type"].lower(): x["judgment_type_id"] for x in cursor.fetchall()}


def get_court_mapping(conn: connection) -> dict:
    """Gets map of existing courts from database.
    Returns a dictionary."""
    with conn.cursor() as cursor:
        cursor.execute("""select court_id, court_name from court""")
        return {x["court_name"].lower(): x["court_id"] for x in cursor.fetchall()}


def get_role_mapping(conn: connection) -> dict:
    """Gets map of existing roles from database.
    Returns a dictionary."""
    with conn.cursor() as cursor:
        cursor.execute("""select role_id, role_name from role""")
        return {x["role_name"].lower(): x["role_id"] for x in cursor.fetchall()}
        

def get_chamber_mapping(conn: connection) -> dict:
    """Gets map of existing chambers from database.
    Returns a dictionary."""
    with conn.cursor() as cursor:
        cursor.execute("""select chamber_name, chamber_id from chamber""")
        return {x["chamber_name"].lower(): x["chamber_id"] for x in cursor.fetchall()}
    

def get_counsel_mapping(conn: connection) -> dict:
    """Gets map of existing counsels from database.
    Returns a dictionary."""
    with conn.cursor() as cursor:
        cursor.execute("""select counsel_name, counsel_id from counsel""")
        return {x["counsel_name"].lower(): x["counsel_id"] for x in cursor.fetchall()}


def get_base_maps(conn: connection) -> dict[dict]:
    """Gets base maps from database.
    Returns a dictionary of dictionaries."""
    role_mapping = get_role_mapping(conn)
    chamber_mapping = get_chamber_mapping(conn)
    court_mapping = get_court_mapping(conn)
    judgment_type_mapping = get_judgment_type_mapping(conn)
    counsel_mapping = get_counsel_mapping(conn)
    return {
        "role_map" : role_mapping,
        "chamber_map" : chamber_mapping,
        "court_map" : court_mapping,
        "judgment_type_map": judgment_type_mapping,
        "counsel_map": counsel_mapping
        }

def seed_db_base_tables(combined_data: list[dict], conn: connection, base_maps: dict[dict]) -> None:
    """Seeds all the base tables.
    Returns None."""
    cursor = conn.cursor()
    roles = {party['party_role'].lower()
            for case in combined_data
            for party in case['parties']}

    roles = [(role,) for role in roles if role not in base_maps["role_map"]]
    role_insert_query = """insert into role (role_name) values %s returning role_id, role_name"""
    execute_values(cursor, role_insert_query, roles)
    conn.commit()


    courts = {(case['court_name'].lower())
                for case in combined_data
                }
    courts = [(court,) for court in courts if court not in base_maps["court_map"]]
    court_insert_query = """insert into court
                            (court_name) 
                            values %s 
                            returning court_id, court_name"""
    execute_values(cursor, court_insert_query, courts)
    conn.commit()

    chambers = {
        (counsel['chamber_name'].lower())
        for case in combined_data
        for party in case['parties']
        for counsel in party['counsels']
    }
    chambers = [(chamber,) for chamber in chambers if chamber not in base_maps["chamber_map"]]
    chambers_insert_query = """insert into chamber
                                (chamber_name) 
                                values %s 
                                returning chamber_id, chamber_name"""
    execute_values(cursor, chambers_insert_query, chambers)
    
    conn.commit()
    cursor.close()


def insert_judgment_table(conn: connection, cursor: connection.cursor, judgment_table_data: list[tuple]) -> None:
    """Inserts judgment table data into judgment table.
    Returns None."""
    judgment_table_insert_query = """insert into judgment
    values %s"""
    execute_values(cursor, judgment_table_insert_query,
                judgment_table_data)
    conn.commit()


def insert_party_table(conn: connection, cursor: connection.cursor, party_table_data: list[tuple]) -> dict:
    """Inserts party table data into party table.
    Returns map of party names and ids."""
    party_table_insert_query = """insert into party (party_name, role_id, neutral_citation)
                                                values %s returning party_name, party_id"""
    execute_values(cursor, party_table_insert_query,
                party_table_data)
    conn.commit()
    party_map = {x["party_name"].lower(): x["party_id"] for x in cursor.fetchall()}
    return party_map


def insert_counsel_table(conn: connection, cursor: connection.cursor, counsel_table_data: list[tuple]) -> dict:
    """Inserts counsel table data into counsel table.
    Returns map of new counsel names and ids."""
    counsel_table_insert_query = """insert into counsel (counsel_name, chamber_id)
                                                values %s returning counsel_name, counsel_id"""
    execute_values(cursor, counsel_table_insert_query, counsel_table_data)
    conn.commit()
    counsel_map = {x["counsel_name"].lower(): x["counsel_id"] for x in cursor.fetchall()}
    return counsel_map


def insert_counsel_assignment_table(conn: connection, cursor: connection.cursor, counsel_assignment_table_data: list[tuple]) -> None:
    """Inserts counsel assignment table data into counsel assignment table.
    Returns None."""
    counsel_assignment_insert_query = """insert into counsel_assignment
                                                    (party_id,counsel_id)
                                                    values %s"""
    execute_values(cursor, counsel_assignment_insert_query,
                counsel_assignment_table_data)
    conn.commit()


def seed_judgment_data(conn: connection, combined_data: list[dict],
                       base_maps: dict[dict, dict]) -> None:
    """Seeds judgment data into database.
    Returns None."""
    role_map = base_maps["role_map"]
    chamber_map = base_maps["chamber_map"]
    court_map = base_maps["court_map"]
    judgment_type_map = base_maps["judgment_type_map"]
    counsel_map = base_maps["counsel_map"]

    for case in combined_data:
        judgment_table_data = []
        party_table_data = []
        counsel_table_data = []
        counsel_assignment_table_data = []

        in_favour_of = case['ruling'].lower()
        judgment_type = case['type_of_crime'].lower()
        judgment_date = case['judgment_date']
        judge_name = case['judge']
        neutral_citation = case['neutral_citation']
        judgment_summary = case['judgment_description']
        court_name = case['court_name'].lower()
        if court_name and judgment_date and neutral_citation and \
            court_map.get(court_name) and role_map.get(in_favour_of.lower()) and \
            judgment_type_map.get(judgment_type):
            for party in case['parties']:
                party_name = party['party_name']
                party_role = party['party_role'].lower()
                party_table_data.append((party_name,
                                        role_map[party_role],
                                        neutral_citation))
                for counsel in party['counsels']:
                    chamber_id = chamber_map[counsel['chamber_name'].lower()]
                    counsel_name = counsel['counsel_name'].lower()
                    if counsel_name not in counsel_map:
                        counsel_table_data.append((counsel_name, chamber_id))
            judgment_table_data.append((neutral_citation,
                                        court_map.get(court_name),
                                        judgment_date,
                                        judgment_summary,
                                        role_map.get(in_favour_of.lower()),
                                        judgment_type_map.get(judgment_type),
                                        judge_name))

            with conn.cursor() as cursor:
                insert_judgment_table(conn, cursor, judgment_table_data)
                party_map = insert_party_table(conn, cursor, party_table_data)
                new_counsel_map = insert_counsel_table(conn, cursor, counsel_table_data)
                counsel_map.update(new_counsel_map)
            for party in case['parties']:
                party_id = party_map[party['party_name'].lower()]
                for counsel in party['counsels']:
                    counsel_id = counsel_map[counsel['counsel_name'].lower()]
                    counsel_assignment_table_data.append((party_id, counsel_id))
            with conn.cursor() as cursor:
                insert_counsel_assignment_table(conn, cursor, counsel_assignment_table_data)


async def create_client(aws_access_key_id: str, aws_secret_access_key: str) -> BaseClient:
    """Returns a BaseClient object for s3 service specified by the provided keys."""
    try:
        config = Config(
            retries = {'max_attempts': 10},  
            max_pool_connections = 50 
        )
        s3_client = client("s3", aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key,
                           config=config)
        logging.info("Successfully connected to s3.")
        return s3_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", str(e))
        raise


async def upload_file_to_s3(s3_client: BaseClient, local_file_path: str, bucket_name: str, s3_key: str) -> None:
    """Uploads a locally saved file to an S3 bucket."""
    try:
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")
        with open(local_file_path, 'rb') as file:
            await asyncio.to_thread(
                s3_client.put_object,
                Bucket=bucket_name,
                Key=s3_key,
                Body=file
            )
        logging.info("File '%s' uploaded successfully to '%s/%s'", local_file_path, bucket_name, s3_key)
    except FileNotFoundError as e:
        logging.error("Error: %s", str(e))
        raise
    except BotoCoreError as e:
        logging.error("AWS S3 error while uploading file '%s' to '%s/%s': %s", local_file_path, bucket_name, s3_key, str(e))
        raise


async def upload_multiple_files_to_s3(s3_client: BaseClient, folder_path: str, bucket_name: str) -> None:
    """Uploads multiple files to S3 concurrently.

    Args:
        s3_client (BaseClient): The S3 client.
        folder_path: str. The folder in which the judgment files are currently saved.
        bucket_name (str): The S3 bucket name.
    """
    files = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, file) for file in files]
    upload_tasks = [
        upload_file_to_s3(s3_client, file_path, bucket_name, file)
        for (file, file_path) in zip(files, file_paths)
    ]
    await asyncio.gather(*upload_tasks)
      




