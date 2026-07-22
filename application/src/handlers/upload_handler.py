import json
import logging
from typing import Any
from src.repositories.s3_repository import S3Repository
from src.repositories.dynamodb_repository import DynamoDBRepository
from src.services.ingestion_service import IngestionService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cold Start Optimization: Initialize dependencies in the global scope
s3_repo = S3Repository()
dynamodb_repo = DynamoDBRepository()
ingestion_service = IngestionService(s3_repo, dynamodb_repo)

def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda Handler for processing file upload requests.
    Strict responsibility: API Gateway interface, secure parsing, and basic validation.
    """
    try:
        # Secure parse of the request body
        body_str = event.get("body", "{}")
        if not body_str:
            body_str = "{}"
            
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON format in request body."})
        }

    # Basic Validation
    user_id = body.get("user_id")
    filename = body.get("filename")

    if not user_id or not filename:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing required fields: 'user_id' and 'filename'."})
        }

    try:
        # Invoke Service Layer
        result = ingestion_service.process_upload_request(user_id=user_id, filename=filename)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    except Exception:
        # Error blinding: Log internally, return generic error to client
        logger.exception("Internal error processing upload request.")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "An internal server error occurred."})
        }
