import unittest
from unittest.mock import patch, MagicMock

import pytest
from botocore.exceptions import ClientError

from judgment_reader_contact_lambda import create_client, get_subscribed_emails, handler


class TestJudgmentReaderContactLambda(unittest.TestCase):

    @patch("judgment_reader_contact_lambda.client")
    def test_create_client_success(self, mock_client):
        mock_client.return_value = MagicMock()

        ses_client = create_client("access_key", "secret_key")

        mock_client.assert_called_once_with(
            "sesv2",
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key",
            region_name="eu-west-2"
        )
        self.assertIsNotNone(ses_client)

    @patch("judgment_reader_contact_lambda.client", side_effect=Exception("Client error"))
    def test_create_client_failure(self, mock_client):
        with self.assertRaises(Exception):
            create_client("access_key", "secret_key")


    def test_get_subscribed_emails(self):
        contact_list_name = 'test-contact-list'
        expected_emails = ['test1@example.com', 'test2@example.com']
        mock_ses_client = MagicMock()
        mock_ses_client.list_contacts.side_effect = [
            {
                'Contacts': [
                    {'EmailAddress': 'test1@example.com'},
                    {'EmailAddress': 'test2@example.com'}
                ],
                'NextToken': None
            }
        ]

        result = get_subscribed_emails(mock_ses_client, contact_list_name)

        assert result == expected_emails
        mock_ses_client.list_contacts.assert_called_with(ContactListName=contact_list_name)
    

    def test_get_subscribed_emails_client_error(self):
        contact_list_name = 'test-contact-list'
        mock_ses_client = MagicMock()
        mock_ses_client.list_contacts.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'InternalServerError',
                    'Message': 'An internal error occurred.'
                }
            },
            operation_name='ListContacts'
        )

        with pytest.raises(ClientError):
            get_subscribed_emails(mock_ses_client, contact_list_name)

    @patch("judgment_reader_contact_lambda.create_client")
    @patch("judgment_reader_contact_lambda.get_subscribed_emails")
    def test_handler(self, mock_get_emails, mock_create_client):
        mock_create_client.return_value = MagicMock()
        mock_get_emails.return_value = ["email@example.com"]

        with patch.dict("judgment_reader_contact_lambda.ENV", {
            "ACCESS_KEY": "access_key",
            "SECRET_KEY": "secret_key",
            "CONTACT_LIST_NAME": "test_list"
        }):
            response = handler({}, {})

        self.assertEqual(response["StatusCode"], 200)
        self.assertIn("email@example.com", response["SubscribedEmails"])
        mock_create_client.assert_called_once()
        mock_get_emails.assert_called_once()
