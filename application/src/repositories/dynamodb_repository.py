import logging
from typing import Any
import boto3
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
