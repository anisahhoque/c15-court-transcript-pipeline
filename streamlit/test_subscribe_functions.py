"""Test file for subscribe_functions"""

import unittest
from unittest.mock import patch, MagicMock
from subscribe_functions import is_valid_email, create_client, create_contact
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


class TestSubscribeFunctions(unittest.TestCase):
    def test_is_valid_email_valid(self):
        valid_email = "test.email@example.com"
        result = is_valid_email(valid_email)
        self.assertTrue(result)

    def test_is_valid_email_invalid(self):
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "missingatsymbol.com",
            "missingdomain@.com",
            "missinglocal@domain",
            "specialchar@@example.com"
        ]
        for email in invalid_emails:
            self.assertFalse(is_valid_email(email), f"Expected {email} to be invalid")

    @patch("subscribe_functions.client")
    def test_create_client_success(self, mock_client):
        mock_client.return_value = MagicMock()
        aws_access_key = "test_access_key"
        aws_secret_key = "test_secret_key"
        result = create_client(aws_access_key, aws_secret_key)
        mock_client.assert_called_once_with(
            "sesv2",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region="eu-west-2"
        )
        self.assertIsNotNone(result)  

    @patch("subscribe_functions.client", side_effect=NoCredentialsError())
    def test_create_client_no_credentials_error(self, mock_client):
        aws_access_key = "test_access_key"
        aws_secret_key = "test_secret_key"
        with self.assertRaises(NoCredentialsError):
            create_client(aws_access_key, aws_secret_key)

    @patch("subscribe_functions.client", side_effect=PartialCredentialsError(provider="test", cred_var="test_var"))
    def test_create_client_partial_credentials_error(self, mock_client):
        aws_access_key = "test_access_key"
        aws_secret_key = "test_secret_key"
        with self.assertRaises(PartialCredentialsError):
            create_client(aws_access_key, aws_secret_key)

    @patch("subscribe_functions.is_valid_email", return_value=True)
    def test_create_contact_success(self, mock_is_valid_email):
        mock_ses_client = MagicMock()
        contact_list_name = "test_contact_list"
        test_email = "test@example.com"
        create_contact(mock_ses_client, contact_list_name, test_email)
        mock_is_valid_email.assert_called_once_with(test_email)
        mock_ses_client.create_contact.assert_called_once_with(
            ContactListName=contact_list_name,
            EmailAddress=test_email,
            TopicPreferences=[
                {
                    'TopicName': 'daily-update',
                    'SubscriptionStatus': 'OPT_IN'
                }
            ],
            UnsubscribeAll=False
        )
        
    @patch("subscribe_functions.is_valid_email", return_value=False)
    def test_create_contact_invalid_email(self, mock_is_valid_email):
        mock_ses_client = MagicMock()
        contact_list_name = "test_contact_list"
        invalid_email = "invalid_email.com"
        with self.assertRaises(ValueError) as context:
            create_contact(mock_ses_client, contact_list_name, invalid_email)
        mock_is_valid_email.assert_called_once_with(invalid_email)
        self.assertEqual(str(context.exception), "Invalid email - please check the email you've entered.")
        mock_ses_client.create_contact.assert_not_called()
