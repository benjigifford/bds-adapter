import os
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from bds_adapter.s3 import S3Handler

@pytest.fixture
def mock_boto3_client():
    """Create mock boto3 client."""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

@pytest.fixture
def s3_handler(mock_boto3_client):
    """Create S3 handler with mocked client."""
    return S3Handler('test-bucket', 'test-prefix')

@pytest.fixture
def temp_file(tmp_path):
    """Create temporary test file."""
    test_file = tmp_path / "test.json"
    test_file.write_text('{"test": "data"}')
    return str(test_file)

def test_upload_file(s3_handler, mock_boto3_client, temp_file):
    """Test successful file upload."""
    result = s3_handler.upload_file(temp_file, 'test.json')
    assert result is True
    mock_boto3_client.upload_file.assert_called_once()

def test_upload_file_error(s3_handler, mock_boto3_client, temp_file):
    """Test file upload with error."""
    mock_boto3_client.upload_file.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'upload_file'
    )
    result = s3_handler.upload_file(temp_file, 'test.json')
    assert result is False

def test_download_file(s3_handler, mock_boto3_client, tmp_path):
    """Test successful file download."""
    local_path = str(tmp_path / "download.json")
    result = s3_handler.download_file('test.json', local_path)
    assert result is True
    mock_boto3_client.download_file.assert_called_once()

def test_download_file_error(s3_handler, mock_boto3_client, tmp_path):
    """Test file download with error."""
    local_path = str(tmp_path / "download.json")
    mock_boto3_client.download_file.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'download_file'
    )
    result = s3_handler.download_file('test.json', local_path)
    assert result is False