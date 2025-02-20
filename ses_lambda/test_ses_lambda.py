import unittest
from unittest.mock import patch, MagicMock, Mock
from ses_lambda import create_client, get_db_connection, get_yesterdays_judgments, handler
from psycopg2 import DatabaseError
from psycopg2.extras import RealDictCursor


class TestSesLambda(unittest.TestCase):

    @patch("ses_lambda.psycopg2.connect")
    def test_get_db_connection_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = get_db_connection("test_db", "user", "password", "localhost", "5432")

        self.assertEqual(result, mock_conn)
        mock_connect.assert_called_once_with(
            dbname="test_db",
            user="user",
            password="password",
            host="localhost",
            port="5432",
            cursor_factory=RealDictCursor
        )

    @patch("ses_lambda.psycopg2.connect", side_effect=DatabaseError)
    def test_get_db_connection_failure(self, mock_connect):
        with self.assertRaises(DatabaseError):
            get_db_connection("test_db", "user", "password", "localhost", "5432")

    @patch("ses_lambda.client")
    def test_create_client_success(self, mock_client):
        mock_client.return_value = MagicMock()

        ses_client = create_client("access_key", "secret_key")

        mock_client.assert_called_once_with(
            "sesv2",
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key"
        )
        self.assertIsNotNone(ses_client)

    @patch("ses_lambda.client", side_effect=Exception("Client error"))
    def test_create_client_failure(self, mock_client):
        with self.assertRaises(Exception):
            create_client("access_key", "secret_key")

    @patch("ses_lambda.get_db_connection")
    @patch("ses_lambda.create_client")
    @patch("ses_lambda.get_subscribed_emails")
    @patch("ses_lambda.get_yesterdays_judgments")
    def test_handler(self, mock_get_judgments, mock_get_emails, mock_create_client, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.return_value = MagicMock()
        mock_create_client.return_value = MagicMock()
        mock_get_judgments.return_value = ["JUDGMENT001", "JUDGMENT002"]
        mock_get_emails.return_value = ["email@example.com"]

        with patch.dict("ses_lambda.ENV", {
            "ACCESS_KEY": "access_key",
            "SECRET_KEY": "secret_key",
            "DB_NAME": "db_name",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "CONTACT_LIST_NAME": "test_list"
        }):
            response = handler({}, {})

        self.assertEqual(response["StatusCode"], 200)
        self.assertIn("JUDGMENT001", response["JudgmentData"])
        self.assertIn("email@example.com", response["SubscribedEmails"])
        mock_create_client.assert_called_once()
        mock_get_db_connection.assert_called_once()
        mock_get_judgments.assert_called_once()
        mock_get_emails.assert_called_once()


    @patch("ses_lambda.psycopg2.connect") 
    def test_get_yesterdays_judgments(self, mock_connect):
        mock_connection = MagicMock()  
        mock_cursor = MagicMock()  
        mock_connect.return_value = mock_connection  
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor  

        mock_cursor.fetchall.return_value = [
            {'neutral_citation': 'JUDGMENT001'},
            {'neutral_citation': 'JUDGMENT002'}
        ]

        conn = mock_connect.return_value  
        result = get_yesterdays_judgments(conn)

        mock_cursor.execute.assert_called_once_with(
            """SELECT neutral_citation
    FROM judgment
    WHERE judgment_date = CURRENT_DATE - INTERVAL '1 day'"""
        )  

        mock_cursor.fetchall.assert_called_once()  
        self.assertEqual(result, ['JUDGMENT001', 'JUDGMENT002'])  


