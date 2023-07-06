FROM python:3.9-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN pip install --upgrade pip

WORKDIR /app
COPY ./app /app
COPY requirements.txt .
RUN pip install -r requirements.txt
