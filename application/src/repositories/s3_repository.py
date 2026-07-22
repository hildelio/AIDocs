import logging
import boto3
from botocore.exceptions import ClientError
from src.config import S3_BUCKET_NAME

logger = logging.getLogger(__name__)

class S3Repository:
    def __init__(self) -> None:
        self.s3_client = boto3.client("s3")
        self.bucket_name = S3_BUCKET_NAME

    def generate_presigned_url(self, user_id: str, filename: str, expiration: int = 3600) -> str:
        """
        Generates a pre-signed URL for uploading a file to S3.
        The S3 key ensures logical isolation per user.
        """
        object_name = f"{user_id}/{filename}"
        
        try:
            response = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name
                },
                ExpiresIn=expiration
            )
            return response
        except ClientError:
            logger.exception(f"Error generating presigned URL for {object_name}")
            raise
