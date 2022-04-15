import os
import boto3
from botocore.client import ClientError
from botocore.config import Config
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath("..")
MODELS_DIR = os.path.realpath("models/savedmodels")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

s3 = boto3.resource(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_USERNAME"),
    aws_secret_access_key=os.getenv("MINIO_PWD"),
    config=Config(signature_version="s3v4"),
    region_name=os.getenv("REGION")
)

try:
    if (
            s3.Bucket(os.getenv("MODELS_BUCKET"))
            and s3.Bucket(os.getenv("IMAGES_BUCKET")) not in s3.buckets.all()
    ):
        print("Creating buckets...")
        s3.create_bucket(
            Bucket=os.getenv("MODELS_BUCKET"),
            CreateBucketConfiguration={"LocationConstraint": os.getenv("REGION")},
        )

        s3.create_bucket(
            Bucket=os.getenv("IMAGES_BUCKET"),
            CreateBucketConfiguration={"LocationConstraint": os.getenv("REGION")},
        )
        s3.Bucket(os.getenv("IMAGES_BUCKET"))
except ClientError as err:
    print("An exception occurred ::", err)


def upload_files(path):
    session = boto3.Session(
        aws_access_key_id=os.getenv("MINIO_USERNAME"),
        aws_secret_access_key=os.getenv("MINIO_PWD"),
        region_name=os.getenv("REGION"),
    )
    bucket = s3.Bucket(os.getenv("MODELS_BUCKET"))

    for subdir, dirs, files in os.walk(MODELS_DIR):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, "rb") as data:
                bucket.put_object(Key=full_path[len(path) + 1:], Body=data)


try:
    print("Uploading models to S3...")
    upload_files(MODELS_DIR)
    print("Uploading finished...")
except ClientError as e:
    print("An exception occurred ::", e)
