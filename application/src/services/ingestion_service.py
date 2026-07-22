import uuid
from datetime import datetime, timezone
from typing import Any
from src.repositories.s3_repository import S3Repository
from src.repositories.dynamodb_repository import DynamoDBRepository

class IngestionService:
    def __init__(self, s3_repository: S3Repository, dynamodb_repository: DynamoDBRepository) -> None:
        self.s3_repository = s3_repository
        self.dynamodb_repository = dynamodb_repository

    def process_upload_request(self, user_id: str, filename: str) -> dict[str, Any]:
        """
        Orchestrates the upload request process:
        - Generates a unique document ID.
        - Gets a pre-signed URL from S3.
        - Saves the initial metadata state to DynamoDB.
        - Returns the document ID and upload URL.
        """
        document_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        presigned_url = self.s3_repository.generate_presigned_url(user_id, filename)
        
        metadata = {
            "id": document_id,
            "user_id": user_id,
            "filename": filename,
            "s3_key": f"{user_id}/{filename}",
            "created_at": created_at,
            "status": "PENDING_UPLOAD"
        }
        
        self.dynamodb_repository.save_metadata(metadata)
        
        return {
            "document_id": document_id,
            "upload_url": presigned_url
        }
