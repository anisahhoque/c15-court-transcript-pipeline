import unittest
from unittest.mock import patch, MagicMock
from judgment_reader_report_lambda import get_db_connection, get_yesterdays_judgments, handler
from psycopg2 import DatabaseError
from psycopg2.extras import RealDictCursor


class TestJudgmentReaderReportLambda(unittest.TestCase):

    @patch("judgment_reader_report_lambda.psycopg2.connect")
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
            cursor_factory=RealDictCursor,
            connect_timeout=30
        )

    @patch("judgment_reader_report_lambda.psycopg2.connect", side_effect=DatabaseError)
    def test_get_db_connection_failure(self, mock_connect):
        with self.assertRaises(DatabaseError):
            get_db_connection("test_db", "user", "password", "localhost", "5432")


    @patch("judgment_reader_report_lambda.get_db_connection")
    @patch("judgment_reader_report_lambda.get_yesterdays_judgments")
    def test_handler(self, mock_get_judgments, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.return_value = MagicMock()
        mock_get_judgments.return_value = ["JUDGMENT001", "JUDGMENT002"]

        with patch.dict("judgment_reader_report_lambda.ENV", {
            "DB_NAME": "db_name",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }):
            response = handler({}, {})

        self.assertEqual(response["StatusCode"], 200)
        self.assertIn("JUDGMENT001", response["JudgmentData"])
        mock_get_db_connection.assert_called_once()
        mock_get_judgments.assert_called_once()


    @patch("judgment_reader_report_lambda.psycopg2.connect") 
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


