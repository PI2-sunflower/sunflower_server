FROM python:3.6

RUN pip3 install --upgrade pip

RUN mkdir -p /sunserver
WORKDIR /sunserver

ADD . /sunserver/
RUN pip3 install -r requirements/dev.txt

ENV PYTHONUNBUFFERED 1
