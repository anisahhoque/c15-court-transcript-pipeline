# pylint:disable=unused-variable
# pylint:disable=unused-argument
from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


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


def get_yesterdays_judgments(conn: connection) -> list[str]:
    """Gets neutral citations of previous day's judgments."""
    query = """SELECT neutral_citation
    FROM judgment
    WHERE judgment_date = CURRENT_DATE - INTERVAL '1 day'"""
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row['neutral_citation'] for row in rows]
    

def get_subscribed_emails(ses_client: BaseClient, contact_list_name: str) -> list[str]:
    """Returns a list of emails that have subscribed to the contact list."""
    contacts = []
    next_token = None
    
    try:
        while True:
            response = ses_client.list_contacts(
                ContactListName=contact_list_name,
                PageSize=50, 
                NextToken=next_token
            )
            
            for contact in response.get('Contacts', []):
                contacts.append(contact['EmailAddress'])
            
            next_token = response.get('NextToken')
            if not next_token:
                break
                
    except ClientError as e:
        print(f"Error retrieving contacts: {e}")
    
    return contacts


def create_client(aws_access_key_id: str, aws_secret_access_key: str) -> BaseClient:
    """Returns a BaseClient object for ses service specified by the provided keys."""
    try:
        ses_client = client("sesv2", aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key)
        logging.info("Successfully connected to ses.")
        return ses_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", str(e))
        raise


def get_judgment_html_hyperlinks(judgments: list[str]) -> str:
    """Returns html string containing hyperlinks to previous day's judgments."""
    html_str = ""
    for judgment in judgments:
        html_content += f"<a href='http://judgment-reader-server-1125183899.eu-west-2.elb.amazonaws.com/Explore_Judgments?neutration_citation={judgment}#case-overview'>{judgment}</a><br>"
    return html_str


def handler(event, context):
    load_dotenv()
    ses_client = create_client(ENV['ACCESS_KEY'], ENV['SECRET_KEY'])
    with get_db_connection(dbname=ENV['DB_NAME'], user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'], host=ENV['DB_HOST'],
                            port=ENV['DB_PORT']) as conn:
        yesterdays_judgments = get_yesterdays_judgments(conn)
        subscribed_emails = get_subscribed_emails(ses_client, ENV['CONTACT_LIST_NAME'])
        judgment_data = get_judgment_html_hyperlinks(yesterdays_judgments)

        return {
            "StatusCode": 200,
            "SubscribedEmails": subscribed_emails,
            "JudgmentData": judgment_data
        }
