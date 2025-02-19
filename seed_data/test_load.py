import psycopg2.extras
import pytest
from unittest import mock
import psycopg2
from load import get_judgment_type_mapping, get_db_connection, get_court_mapping, get_counsel_mapping, get_chamber_mapping, get_role_mapping, get_base_maps

def test_get_db_connection_successfully():
    mock_conn = mock.MagicMock(spec=psycopg2.extensions.connection)
    with mock.patch("psycopg2.connect", return_value=mock_conn) as mock_connect:
        conn = get_db_connection("dbname", "user", "password", "host", "port")

        mock_connect.assert_called_once_with(
            dbname="dbname", user="user", password="password",
            host="host", port="port", cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    assert conn == mock_conn

def test_get_db_connection_unsuccessful():

    with mock.patch("psycopg2.connect", side_effect=psycopg2.DatabaseError("Connection failed")) as mock_connect:
        try:
            get_db_connection("dbname", "user", "password", "host", "port")
        except psycopg2.DatabaseError as e:
            assert str(e) == "Error connecting to database."



def test_get_judgment_type_mapping_valid_case():
    """    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor"""


    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        { 'judgment_type':'civil', 'judgment_type_id':1},
        { 'judgment_type':'criminal', 'judgment_type_id':2}
    ]

    result = get_judgment_type_mapping(mock_conn)
    
    expected_result = {
        'civil': 1,
        'criminal': 2
    }
    assert result == expected_result
    
def test_get_court_mapping_valid_case():
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        { 'court_name':'high court of justice', 'court_id':1},
        { 'court_name':'crown court', 'court_id':2},
        { 'court_name':'supreme court', 'court_id':3}
    ]

    result = get_court_mapping(mock_conn)
    
    expected_result = {
        'high court of justice': 1,
        'crown court': 2,
        'supreme court': 3
    }
    assert result == expected_result

def test_get_role_mapping_valid_case():
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        { 'role_name':'respondent', 'role_id':1},
        { 'role_name':'appellant', 'role_id':2},
        { 'role_name':'defendant', 'role_id':3}
    ]

    result = get_role_mapping(mock_conn)
    
    expected_result = {
        'respondent': 1,
        'appellant': 2,
        'defendant': 3
    }
    assert result == expected_result

def test_get_counsel_mapping_valid_case():
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        { 'counsel_name':'Xyz', 'counsel_id':1},
        { 'counsel_name':'Abc def', 'counsel_id':2},
        { 'counsel_name':'UVw', 'counsel_id':3}
    ]

    result = get_counsel_mapping(mock_conn)
    
    expected_result = {
        'xyz': 1,
        'abc def': 2,
        'uvw': 3
    }
    assert result == expected_result

def test_get_chamber_mapping_valid_case():
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        { 'chamber_name':'Xyz', 'chamber_id':1},
        { 'chamber_name':'Abc def', 'chamber_id':2},
        { 'chamber_name':'UVw', 'chamber_id':3}
    ]

    result = get_chamber_mapping(mock_conn)
    
    expected_result = {
        'xyz': 1,
        'abc def': 2,
        'uvw': 3
    }
    assert result == expected_result