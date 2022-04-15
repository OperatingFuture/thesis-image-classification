import os
import boto3
from botocore.client import ClientError
from botocore.config import Config
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath("..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

s3 = boto3.resource(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_USERNAME"),
    aws_secret_access_key=os.getenv("MINIO_PWD"),
    config=Config(signature_version="s3v4"),
    region_name=os.getenv("REGION")
)


def upload_file(local_path, s3_path):
    try:
        s3.Bucket(os.getenv("IMAGES_BUCKET")).upload_file(local_path, s3_path)
    except ClientError as err:
        print("Something Happened: ", err)
        return err
    return {"message:" "Image uploaded!"}


# def upload_file_to_s3():
#     """
#     Docs: https://boto3.readthedocs.io/en/latest/guide/s3.html
#     """
#     bucket = s3.Bucket(os.getenv("IMAGES_BUCKET"))
#     try:
#         s3.upload_file(img, bucket, img_filename, ExtraArgs={'ACL': 'public-read', "ContentType": "image/jpeg"})
#         # bucket.put_object(Body=img, Key=img_filename, ACL='public-read-write', ContentType=img_content_type)
#         # s3.upload_fileobj(
#         #     file,
#         #     bucket_name,
#         #     file.filename
#         # )
#     except ClientError as e:
#         print("Something Happened: ", e)
#         return e
#     return 'http://localhost:9000/' + os.getenv("IMAGES_BUCKET") + '/' + img_filename
