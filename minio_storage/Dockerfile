FROM python:3.8.10


WORKDIR /minio_storage

COPY ./requirements.txt /minio_storage

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /minio_storage

CMD ["python", "./s3_bucket.py"]