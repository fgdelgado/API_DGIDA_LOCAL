import os
import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    ReadTimeoutError,
    ConnectTimeoutError,
)

def get_dynamodb_client():
    # Timeouts bajos para que /health responda rápido
    config = Config(
        connect_timeout=1,   # segundos
        read_timeout=1,      # segundos
        retries={"max_attempts": 1}  # reduce reintentos
    )

    return boto3.client(
        "dynamodb",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
        config=config,
    )

def check_dynamodb_connection():
    endpoint = os.getenv("DYNAMODB_ENDPOINT")
    if not endpoint:
        return {"ok": False, "error": "DYNAMODB_ENDPOINT no está definido"}

    try:
        dynamodb = get_dynamodb_client()
        dynamodb.list_tables()
        return {"ok": True, "status": "connected", "endpoint": endpoint}

    except (EndpointConnectionError, ReadTimeoutError, ConnectTimeoutError) as e:
        return {"ok": False, "error": "timeout/conexión", "details": str(e), "endpoint": endpoint}

    except ClientError as e:
        return {"ok": False, "error": "client_error", "details": e.response["Error"]["Message"], "endpoint": endpoint}

    except Exception as e:
        return {"ok": False, "error": "unknown_error", "details": str(e), "endpoint": endpoint}

def get_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
    )