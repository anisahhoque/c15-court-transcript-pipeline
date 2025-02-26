"Lambda for getting previous day's judgment website links."
# pylint:disable=unused-variable
# pylint:disable=unused-argument
from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


def get_db_connection(dbname: str, user: str, password: str, host: str, port: str) -> connection:
    """Establishes a connection to PostgreSQL.
    Returns a PostgreSQL connection object."""
    try:
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port,
            cursor_factory=RealDictCursor,
            connect_timeout=30)
        return conn
    except psycopg2.DatabaseError as e:
        raise psycopg2.DatabaseError(f"Error connecting to database: {e}") from e


def get_yesterdays_judgments(conn: connection) -> list[str]:
    """Gets neutral citations of previous day's judgments."""
    query = """SELECT neutral_citation
    FROM judgment
    WHERE judgment_date = CURRENT_DATE - INTERVAL '1 day'"""
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row['neutral_citation'] for row in rows]


def get_judgment_html_hyperlinks(judgments: list[str]) -> str:
    """Returns html string containing hyperlinks to previous day's judgments."""
    html_str = ""
    for judgment in judgments:
        html_str += (f"<a href='judgment-reader-server-552138396.eu-west-2.elb.amazonaws.com/"
        f"Explore_Judgments?selected_citation={judgment}#case-overview'>{judgment}</a><br>")
    return html_str


def handler(event, context):
    "Lambda handler function."
    load_dotenv()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    with get_db_connection(dbname=ENV['DB_NAME'], user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'], host=ENV['DB_HOST'],
                            port=ENV['DB_PORT']) as conn:
        yesterdays_judgments = get_yesterdays_judgments(conn)
        judgment_data = get_judgment_html_hyperlinks(yesterdays_judgments)
        return {
            "StatusCode": 200,
            "JudgmentData": judgment_data
        }
