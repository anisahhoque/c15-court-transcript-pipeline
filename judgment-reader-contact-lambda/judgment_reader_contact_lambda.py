"""Lambda to fetch contact list from SES."""
# pylint:disable=unused-variable
# pylint:disable=unused-argument
from os import environ as ENV
import logging

from dotenv import load_dotenv
from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


def get_subscribed_emails(ses_client: BaseClient, contact_list_name: str) -> list[str]:
    """Returns a list of emails that have subscribed to the contact list."""
    emails = []
    next_token = None

    try:
        while True:
            params = {
                'ContactListName': contact_list_name
            }

            if next_token:
                params['NextToken'] = next_token

            response = ses_client.list_contacts(**params)

            contacts = response.get('Contacts', [])
            for contact in contacts:
                emails.append(contact.get('EmailAddress'))

            next_token = response.get('NextToken')

            if not next_token:
                break

        return emails
    except ClientError as e:
        logging.error("Error connecting to client: %s", e)
        raise


def create_client(aws_access_key_id: str, aws_secret_access_key: str) -> BaseClient:
    """Returns a BaseClient object for ses service specified by the provided keys."""
    try:
        ses_client = client("sesv2", aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key,
                           region_name="eu-west-2")
        logging.info("Successfully connected to ses.")
        return ses_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", str(e))
        raise


def handler(event, context):
    """Lambda handler."""
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ses_client = create_client(ENV['ACCESS_KEY'], ENV['SECRET_KEY'])
    subscribed_emails = get_subscribed_emails(ses_client, ENV['CONTACT_LIST_NAME'])
    return {
        "StatusCode": 200,
        "SubscribedEmails": subscribed_emails
    }
