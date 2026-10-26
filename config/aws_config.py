import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME", "hostelhub-media-474333173964")


def get_boto3_session():
    """Return a boto3 Session initialized with env vars or system AWS CLI credentials."""
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", AWS_REGION)

    if access_key and secret_key:
        return boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    # Fallback to AWS CLI configured profiles (~/.aws/credentials or EC2 IAM Role)
    return boto3.Session(region_name=region)


def get_s3_client():
    """Get an S3 client instance or None if credentials are missing."""
    try:
        session = get_boto3_session()
        return session.client("s3")
    except Exception as e:
        print(f"[AWS Config] S3 client error: {e}")
        return None


def get_ec2_client():
    """Get an EC2 client instance or None."""
    try:
        session = get_boto3_session()
        return session.client("ec2")
    except Exception as e:
        print(f"[AWS Config] EC2 client error: {e}")
        return None
