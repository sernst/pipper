FROM continuumio/miniconda3:latest

RUN apt-get update \
 && apt-get install nano \
 && pip install pip --upgrade

COPY requirements.txt /root/requirements.txt

RUN pip install -r /root/requirements.txt

WORKDIR "/root/"
