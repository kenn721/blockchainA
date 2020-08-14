FROM python:3.7-slim

LABEL maintainer the Docker Community

RUN mkdir /src

WORKDIR /src

COPY requirements.txt /src/

RUN pip install -r requirements.txt

COPY . /src/

ENV FLASK_APP /src/node_server.py