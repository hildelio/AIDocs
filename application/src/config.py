import os

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set.")
    return value

# Centralized configuration reading from environment variables (Fail-Fast)
S3_BUCKET_NAME = get_required_env("S3_BUCKET_NAME")
DYNAMODB_TABLE_NAME = get_required_env("DYNAMODB_TABLE_NAME")
