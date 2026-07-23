import logging
import boto3
import time
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class TextractRepository:
    def __init__(self) -> None:
        self.textract_client = boto3.client("textract", region_name="us-east-1")

    def extract_text_from_s3(self, bucket_name: str, object_key: str) -> str:
        """
        Calls Amazon Textract to extract text from a document in S3.
        Concatenates blocks of type 'LINE' and returns the full string.
        """
        try:
            logger.info(f"Calling Textract API for document {object_key}")
            start_time = time.time()
            response = self.textract_client.detect_document_text(
                Document={
                    "S3Object": {
                        "Bucket": bucket_name,
                        "Name": object_key
                    }
                }
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Textract API call completed for document {object_key} in {elapsed_time:.2f} seconds")
            
            extracted_lines = []
            for block in response.get("Blocks", []):
                if block.get("BlockType") == "LINE":
                    extracted_lines.append(block.get("Text", ""))
            
            return "\n".join(extracted_lines)
            
        except ClientError:
            logger.exception(f"Error extracting text from s3://{bucket_name}/{object_key}")
            raise
