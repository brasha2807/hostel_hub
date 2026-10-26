import os
import time
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config.aws_config import get_boto3_session, get_s3_client, get_ec2_client, AWS_REGION, AWS_S3_BUCKET
from config.settings import BASE_DIR, DB_PATH, STATIC_DIR


def check_aws_connection():
    """
    Check if AWS credentials are active and valid via STS get_caller_identity.
    Returns status dict with account details.
    """
    try:
        session = get_boto3_session()
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        return {
            "connected": True,
            "account_id": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
            "region": session.region_name or AWS_REGION,
            "error": None
        }
    except NoCredentialsError:
        return {
            "connected": False,
            "account_id": None,
            "arn": None,
            "user_id": None,
            "region": AWS_REGION,
            "error": "No AWS credentials found. Please set AWS_ACCESS_KEY_ID or configure ~/.aws/credentials."
        }
    except Exception as e:
        return {
            "connected": False,
            "account_id": None,
            "arn": None,
            "user_id": None,
            "region": AWS_REGION,
            "error": str(e)
        }


def list_all_s3_buckets():
    """List all S3 buckets available in the account."""
    s3 = get_s3_client()
    if not s3:
        return []
    try:
        resp = s3.list_buckets()
        return [b["Name"] for b in resp.get("Buckets", [])]
    except Exception as e:
        print(f"[AWS S3] list_buckets error: {e}")
        return []


def check_bucket_status(bucket_name=None):
    """Check if the designated S3 bucket exists and is accessible."""
    target_bucket = bucket_name or AWS_S3_BUCKET
    s3 = get_s3_client()
    if not s3:
        return {"exists": False, "bucket_name": target_bucket, "error": "S3 Client unavailable"}

    all_buckets = list_all_s3_buckets()
    if target_bucket not in all_buckets:
        return {
            "exists": False,
            "bucket_name": target_bucket,
            "all_buckets": all_buckets,
            "error": f"Bucket '{target_bucket}' does not exist yet."
        }

    try:
        s3.head_bucket(Bucket=target_bucket)
        # Count objects
        res = s3.list_objects_v2(Bucket=target_bucket, MaxKeys=100)
        obj_count = res.get("KeyCount", 0)
        return {
            "exists": True,
            "bucket_name": target_bucket,
            "all_buckets": all_buckets,
            "object_count": obj_count,
            "error": None
        }
    except ClientError as e:
        return {
            "exists": False,
            "bucket_name": target_bucket,
            "all_buckets": all_buckets,
            "error": str(e)
        }


def create_s3_storage_bucket(bucket_name=None):
    """
    Create an S3 bucket in the configured region (ap-south-1).
    """
    target_bucket = bucket_name or AWS_S3_BUCKET
    s3 = get_s3_client()
    if not s3:
        return False, "S3 client not initialized. Check AWS credentials."

    try:
        session = get_boto3_session()
        region = session.region_name or AWS_REGION

        if region == "us-east-1":
            s3.create_bucket(Bucket=target_bucket)
        else:
            s3.create_bucket(
                Bucket=target_bucket,
                CreateBucketConfiguration={"LocationConstraint": region}
            )

        # Enable default server-side AES256 encryption
        try:
            s3.put_bucket_encryption(
                Bucket=target_bucket,
                ServerSideEncryptionConfiguration={
                    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
                }
            )
        except Exception:
            pass

        return True, f"Bucket '{target_bucket}' created successfully in {region}!"
    except Exception as e:
        return False, str(e)


def upload_file_to_s3(local_path, s3_key, bucket_name=None):
    """Upload a local file to S3."""
    target_bucket = bucket_name or AWS_S3_BUCKET
    s3 = get_s3_client()
    if not s3:
        return False, "S3 client unavailable."

    if not os.path.exists(local_path):
        return False, f"File {local_path} not found."

    try:
        s3.upload_file(local_path, target_bucket, s3_key)
        return True, f"Uploaded to s3://{target_bucket}/{s3_key}"
    except Exception as e:
        return False, str(e)


def backup_database_to_s3(bucket_name=None):
    """Create a backup of hostel_hub.db and upload to S3."""
    if not os.path.exists(DB_PATH):
        return False, "Database file not found."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"backups/hostel_hub_backup_{timestamp}.db"
    return upload_file_to_s3(DB_PATH, s3_key, bucket_name)


def get_ec2_instances_summary():
    """Describe EC2 instances running in the configured region."""
    ec2 = get_ec2_client()
    if not ec2:
        return []
    try:
        resp = ec2.describe_instances()
        instances = []
        for res in resp.get("Reservations", []):
            for inst in res.get("Instances", []):
                name_tag = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), "Unnamed")
                instances.append({
                    "id": inst.get("InstanceId"),
                    "name": name_tag,
                    "type": inst.get("InstanceType"),
                    "state": inst.get("State", {}).get("Name"),
                    "public_ip": inst.get("PublicIpAddress", "N/A"),
                    "private_ip": inst.get("PrivateIpAddress", "N/A"),
                    "launch_time": str(inst.get("LaunchTime", ""))[:19]
                })
        return instances
    except Exception as e:
        print(f"[AWS EC2] describe_instances error: {e}")
        return []
