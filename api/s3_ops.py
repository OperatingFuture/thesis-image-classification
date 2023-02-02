import io
import os
import zipfile
import boto3
from botocore.client import ClientError
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

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


def upload_img_to_s3(img, filename, content_type):
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
    image = load_img(io.BytesIO(image.get()['Body'].read()), target_size=(32, 32))
    image = img_to_array(image)
    image = image.reshape(1, 32, 32, 3)
    image = image.astype('float32')
    image = image / 255.0
    return image

def load_model_from_s3(model_name: str):
    bucket = s3_resource.Bucket("saved-models")
    # Fetch and save the zip file to the temporary directory
    bucket.download_file(f"{model_name}.zip", f"{model_name}.zip")
    # Extract the model zip file within the temporary directory
    with zipfile.ZipFile(f"{model_name}.zip") as zip_ref:
        zip_ref.extractall(f"{model_name}")
    # Load the keras model from the temporary directory
    return load_model(os.path.join("model_final/model_final", "custom_cnn_final.h5"))
