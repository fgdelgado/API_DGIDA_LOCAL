import os
import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    ReadTimeoutError,
    ConnectTimeoutError,
)

def is_aws():
    return os.getenv("AWS_EXECUTION_ENV") is not None

def get_dynamodb_client():
    config = Config(
        connect_timeout=1,
        read_timeout=1,
        retries={"max_attempts": 1}
    )

    if is_aws():
        # AWS DynamoDB (SIN endpoint_url)
        return boto3.client(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=config,
        )
    else:
        # DynamoDB Local
        return boto3.client(
            "dynamodb",
            region_name="us-east-1",
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
            config=config,
        )

def get_dynamodb_resource():
    if is_aws():
        return boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
    else:
        return boto3.resource(
            "dynamodb",
            region_name="us-east-1",
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )

def check_dynamodb_connection():
    try:
        dynamodb = get_dynamodb_client()
        dynamodb.list_tables()

        return {
            "ok": True,
            "env": "aws" if is_aws() else "local"
        }

    except (EndpointConnectionError, ReadTimeoutError, ConnectTimeoutError) as e:
        return {"ok": False, "error": "timeout/conexion", "details": str(e)}

    except ClientError as e:
        return {"ok": False, "error": "client_error", "details": e.response["Error"]["Message"]}

    except Exception as e:
        return {"ok": False, "error": "unknown_error", "details": str(e)}
