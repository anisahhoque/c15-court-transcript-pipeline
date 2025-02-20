"""Functions to create email contact when subscribe button is pressed."""
import re
import logging

from boto3 import client
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def is_valid_email(email):
    """Check if the given string is a valid email."""
    email_regex = re.compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
    r"\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@"
    r"(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|"
    r"\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}"
    r"(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|"
    r"[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|"
    r"\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
)
    return re.fullmatch(email_regex, email) is not None


def create_client(aws_access_key_id: str, aws_secret_access_key: str) -> BaseClient:
    """Returns a BaseClient object for s3 service specified by the provided keys."""
    try:
        ses_client = client("sesv2", aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key)
        logging.info("Successfully connected to ses.")
        return ses_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", str(e))
        raise


def create_contact(ses_client: BaseClient, contact_list_name: str, email: str) -> None:
    """Creates contact in given contact list.
    Returns None."""
    if not is_valid_email(email):
        raise ValueError("Invalid email - please check the email you've entered.")
    ses_client.create_contact(
        ContactListName=contact_list_name,
        EmailAddress=email,
        TopicPreferences=[
            {
                'TopicName': 'daily-update',
                'SubscriptionStatus': 'OPT_IN'
            }
        ],
        UnsubscribeAll=False
    )


