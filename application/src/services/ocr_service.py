import logging
from datetime import datetime, timezone
from src.repositories.textract_repository import TextractRepository
from src.repositories.dynamodb_repository import DynamoDBRepository

logger = logging.getLogger(__name__)

class OcrService:
    def __init__(self, textract_repository: TextractRepository, dynamodb_repository: DynamoDBRepository) -> None:
        self.textract_repository = textract_repository
        self.dynamodb_repository = dynamodb_repository

    def process_document(self, bucket_name: str, object_key: str) -> None:
        """
        Orchestrates the OCR processing flow:
        - Retrieves metadata via S3 Key
        - Updates status to PROCESSING
        - Extracts text via Textract
        - Updates metadata with extracted text and PROCESSED status
        """
        document = self.dynamodb_repository.get_document_by_s3_key(object_key)
        
        if not document:
            raise ValueError(f"Document metadata not found for s3_key: {object_key}")
            
        document_id = document["id"]
        
        try:
            # Mark as processing
            self.dynamodb_repository.update_document(
                document_id, 
                {
                    "status": "PROCESSING",
                    "processing_started_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Extract text
            extracted_text = self.textract_repository.extract_text_from_s3(bucket_name, object_key)
            
            # Mark as processed
            self.dynamodb_repository.update_document(
                document_id,
                {
                    "status": "PROCESSED",
                    "extracted_text": extracted_text,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            )
            logger.info(f"Successfully processed document {document_id}")
            
        except Exception:
            logger.exception(f"Failed to process document {document_id}")
            
            # Architectural Decision for MVP: We swallow the exception here to prevent AWS from infinitely retrying the S3 event (Poison Pill), as we don't have a DLQ configured yet. The failure is recorded in DynamoDB.
            
            # Mark as failed in DynamoDB
            try:
                self.dynamodb_repository.update_document(
                    document_id,
                    {"status": "FAILED"}
                )
            except Exception:
                # If even the update fails, just log it so it doesn't crash the handler silently
                logger.exception(f"Failed to update status to FAILED for document {document_id}")
