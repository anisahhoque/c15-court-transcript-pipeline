# pylint:disable=unused-variable
import os
import logging
import psycopg2.extras
import pytest
from unittest.mock import MagicMock, AsyncMock, ANY, patch
import psycopg2
from daily_load import (get_judgment_type_mapping, get_db_connection,
                  get_court_mapping, get_role_mapping, 
                  upload_file_to_s3, upload_multiple_files_to_s3)

def test_get_db_connection_successfully():
    """Test that get_db_connection returns a valid database connection object."""
    mock_conn = MagicMock(spec=psycopg2.extensions.connection)
    with patch("psycopg2.connect", return_value=mock_conn) as mock_connect:
        conn = get_db_connection("dbname", "user", "password", "host", "port")

        mock_connect.assert_called_once_with(
            dbname="dbname", user="user", password="password",
            host="host", port="port", cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    assert conn == mock_conn

def test_get_db_connection_unsuccessful():
    """Test that get_db_connection raises a DatabaseError when connection fails."""
    with patch("psycopg2.connect", side_effect=psycopg2.DatabaseError("Connection failed")) as mock_connect:
        try:
            get_db_connection("dbname", "user", "password", "host", "port")
        except psycopg2.DatabaseError as e:
            assert str(e) == "Error connecting to database."

def test_get_judgment_type_mapping_valid_case():
    """Test that get_judgment_type_mapping correctly maps judgment types to their IDs."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
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
    """Test that get_court_mapping correctly maps court names to their IDs."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
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
    """Test that get_role_mapping correctly maps role names to their IDs."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
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

test_files = [f"test_file_{i}.txt" for i in range(1, 21)]

@pytest.mark.asyncio
@pytest.mark.parametrize("file_name", test_files)
async def test_upload_file_to_s3(file_name):
    """Test that upload_file_to_s3 successfully uploads a file to S3."""
    s3_client = MagicMock()
    bucket_name = "test-bucket"
    s3_key = file_name

    with open(file_name, "w") as f:
        f.write("test data")

    try:
        await upload_file_to_s3(s3_client, file_name, bucket_name, s3_key)
        s3_client.put_object.assert_called_once_with(Bucket=bucket_name, Key=s3_key, Body=ANY)
    finally:
        os.remove(file_name)  

@pytest.mark.asyncio
@pytest.mark.parametrize("num_files", [n for n in range(1, 50, 5)])
async def test_upload_multiple_files_to_s3(num_files):
    """Test that upload_multiple_files_to_s3 uploads multiple files to S3 and calls put_object the correct number of times."""
    s3_client = MagicMock()
    folder_path = "test_folder"
    bucket_name = "test-bucket"
    os.makedirs(folder_path, exist_ok=True)

    test_files = [f"test_file_{i}.txt" for i in range(1, num_files + 1)]

    for file in test_files:
        with open(os.path.join(folder_path, file), "w") as f:
            f.write("test data")

    try:
        await upload_multiple_files_to_s3(s3_client, folder_path, bucket_name)
        assert s3_client.put_object.call_count == num_files
    finally:
        for file in test_files:
            os.remove(os.path.join(folder_path, file))
        os.rmdir(folder_path)

@pytest.mark.asyncio
async def test_upload_file_to_s3_file_not_found(caplog):
    """Test that upload_file_to_s3 logs an error when the file does not exist and does not call put_object."""
    s3_client = AsyncMock()
    local_file_path = "non_existent_file.txt"
    bucket_name = "test-bucket"
    s3_key = "uploaded_file.txt"
    
    with caplog.at_level(logging.ERROR):
        await upload_file_to_s3(s3_client, local_file_path, bucket_name, s3_key)

    s3_client.put_object.assert_not_called()
    
    assert f"Error: File not found: {local_file_path}" in caplog.text
