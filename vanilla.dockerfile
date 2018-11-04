FROM python:3.6

RUN apt-get update \
 && apt-get install nano \
 && pip install pip --upgrade

COPY requirements.txt /root/requirements.txt

RUN pip install -r /root/requirements.txt

WORKDIR "/root/"
