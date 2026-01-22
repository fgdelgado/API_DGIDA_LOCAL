import boto3
import os
from botocore.exceptions import ClientError

def get_dynamodb_client():
    return boto3.client(
        "dynamodb",
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

def check_dynamodb_connection():
    try:
        dynamodb = get_dynamodb_client()
        dynamodb.list_tables()
        return "connected"
    except ClientError as e:
        return f"error: {e.response['Error']['Message']}"
    except Exception as e:
        return f"error: {str(e)}"