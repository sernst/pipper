FROM python:3.6

RUN apt-get update \
 && apt-get install nano \
 && pip install pip --upgrade

WORKDIR "/root/"

