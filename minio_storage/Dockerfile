FROM python:3.8.10

COPY . /minio_storage
WORKDIR /minio_storage

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "./s3_bucket.py"]