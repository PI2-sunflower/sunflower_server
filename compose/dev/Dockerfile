FROM python:3.7-alpine

RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip3 install --upgrade pip

RUN mkdir -p /sunserver
WORKDIR /sunserver

ADD . /sunserver/
RUN pip3 install -r requirements/dev.txt

ENV PYTHONUNBUFFERED 1
