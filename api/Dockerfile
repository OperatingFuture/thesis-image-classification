FROM python:3.10


WORKDIR /api

COPY ./requirements.txt /api

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /api

ENTRYPOINT ["flask", "run"]