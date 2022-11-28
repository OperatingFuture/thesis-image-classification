import os
import io
import boto3
from botocore.client import ClientError
from PIL import Image

s3_resource = boto3.resource(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123"
)

s3 = boto3.client("s3",
                  endpoint_url="http://minio:9000",
                  aws_access_key_id="minio",
                  aws_secret_access_key="minio123")


def upload_file_to_s3(img, filename, content_type):
    """
    Docs: https://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3.put_object(Body=img,
                      Bucket="saved-images",
                      Key=filename,
                      ContentType=content_type)
    except ClientError as e:
        print("Something Happened: ", e)
        return e
    return "http://localhost:9000/saved-images/" + filename


def image_from_s3(filename):
    bucket = s3_resource.Bucket("saved-images")
    image = bucket.Object(filename)
    img_data = image.get().get('Body').read()
    img = Image.open(io.BytesIO(img_data))
    img = img.convert('RGB')
    img = img.resize((224, 224))
    return img
