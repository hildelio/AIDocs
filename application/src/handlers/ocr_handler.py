import logging
import urllib.parse
from typing import Any
from src.repositories.textract_repository import TextractRepository
from src.repositories.dynamodb_repository import DynamoDBRepository
from src.services.ocr_service import OcrService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cold Start Optimization
textract_repo = TextractRepository()
dynamodb_repo = DynamoDBRepository()
ocr_service = OcrService(textract_repo, dynamodb_repo)

def handler(event: dict[str, Any], context: Any) -> None:
    """
    AWS Lambda Handler for S3 Events (ObjectCreated).
    Processes multiple records resiliently.
    """
    records = event.get("Records", [])
    
    for record in records:
        try:
            s3_info = record.get("s3", {})
            bucket_name = s3_info.get("bucket", {}).get("name")
            object_key = s3_info.get("object", {}).get("key")
            
            if not bucket_name or not object_key:
                logger.warning("Missing bucket_name or object_key in S3 record. Skipping.")
                continue
                
            # Decode the object key (S3 replaces spaces with '+' in the event payload)
            decoded_key = urllib.parse.unquote_plus(object_key)
            
            logger.info(f"Processing S3 event for s3://{bucket_name}/{decoded_key}")
            
            # Delegate to the business logic service
            ocr_service.process_document(bucket_name, decoded_key)
            
        except Exception:
            # Resiliency: Isolate failure per record so one bad file doesn't block the rest
            logger.exception("Failed to process S3 record.")
