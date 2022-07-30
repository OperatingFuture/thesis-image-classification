FROM tensorflow/tensorflow:2.7.0


WORKDIR /api

COPY ./requirements.txt /api

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /api

ENTRYPOINT ["flask", "run"]