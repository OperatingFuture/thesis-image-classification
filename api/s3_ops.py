import os
import io
import boto3
from botocore.client import ClientError
from botocore.config import Config
from dotenv import load_dotenv
from PIL import Image

ROOT_DIR = os.path.realpath("..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

s3_resource = boto3.resource(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_USERNAME"),
    aws_secret_access_key=os.getenv("MINIO_PWD"),
    config=Config(signature_version="s3v4"),
    region_name=os.getenv("REGION")
)

s3 = boto3.client('s3', endpoint_url=os.getenv("MINIO_ENDPOINT"),
                  aws_access_key_id=os.getenv("MINIO_USERNAME"),
                  aws_secret_access_key=os.getenv("MINIO_PWD"),
                  region_name=os.getenv("REGION"))


def upload_file_to_s3(img, filename, content_type):
    """
    Docs: https://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3.put_object(Body=img,
                      Bucket=os.getenv("IMAGES_BUCKET"),
                      Key=filename,
                      ContentType=content_type)
    except ClientError as e:
        print("Something Happened: ", e)
        return e
    return 'http://localhost:9000/' + os.getenv("IMAGES_BUCKET") + '/' + filename


def image_from_s3(filename):
    bucket = s3_resource.Bucket(os.getenv("IMAGES_BUCKET"))
    image = bucket.Object(filename)
    img_data = image.get().get('Body').read()
    img = Image.open(io.BytesIO(img_data))
    img = img.convert('RGB')
    img = img.resize((224, 224))
    return img
