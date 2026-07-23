import logging
from typing import Any, Optional
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from src.config import DYNAMODB_TABLE_NAME

logger = logging.getLogger(__name__)

class DynamoDBRepository:
    def __init__(self) -> None:
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)

    def save_metadata(self, item: dict[str, Any]) -> None:
        """
        Saves a metadata record directly into DynamoDB.
        """
        try:
            self.table.put_item(Item=item)
        except ClientError:
            logger.exception("Error saving item to DynamoDB")
            raise

    def get_document_by_s3_key(self, s3_key: str) -> Optional[dict[str, Any]]:
        """
        Retrieves a document by its S3 Key.
        
        IMPORTANT (Production Note): For the MVP, we are using a Scan with 
        a FilterExpression on s3_key. In a production environment, this query 
        MUST utilize a Global Secondary Index (GSI) on s3_key to avoid 
        full table scans and performance issues.
        """
        try:
            response = self.table.scan(
                FilterExpression=Attr("s3_key").eq(s3_key)
            )
            items = response.get("Items", [])
            if items:
                return items[0]
            return None
        except ClientError:
            logger.exception(f"Error retrieving document by s3_key: {s3_key}")
            raise

    def update_document(self, document_id: str, updates: dict[str, Any]) -> None:
        """
        Updates specific attributes of a document.
        Dynamically generates the UpdateExpression.
        """
        if not updates:
            return
            
        update_expr_parts = []
        expr_attr_values = {}
        expr_attr_names = {}
        
        for key, value in updates.items():
            # Use expression attribute names to avoid reserved keyword conflicts (e.g. 'status')
            attr_name = f"#{key}"
            attr_value = f":{key}"
            
            update_expr_parts.append(f"{attr_name} = {attr_value}")
            expr_attr_names[attr_name] = key
            expr_attr_values[attr_value] = value
            
        update_expr = "SET " + ", ".join(update_expr_parts)
        
        try:
            self.table.update_item(
                Key={"id": document_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
        except ClientError:
            logger.exception(f"Error updating document {document_id}")
            raise
