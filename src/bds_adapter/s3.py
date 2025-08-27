from typing import Optional
import boto3
from botocore.exceptions import ClientError

class S3Handler:
    """Handles S3 operations for BDS adapter."""
    
    def __init__(self, bucket: str, prefix: Optional[str] = None):
        """Initialize S3 handler with bucket and optional prefix."""
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.prefix = prefix.rstrip('/') if prefix else ''

    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """Upload a file to S3."""
        try:
            if self.prefix:
                s3_key = f"{self.prefix}/{s3_key}"
            self.s3.upload_file(file_path, self.bucket, s3_key)
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            return False

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download a file from S3."""
        try:
            if self.prefix:
                s3_key = f"{self.prefix}/{s3_key}"
            self.s3.download_file(self.bucket, s3_key, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading from S3: {str(e)}")
            return False