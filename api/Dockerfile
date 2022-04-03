FROM tensorflow/tensorflow:2.7.0

COPY . /api
WORKDIR /api

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT ["flask", "run"]