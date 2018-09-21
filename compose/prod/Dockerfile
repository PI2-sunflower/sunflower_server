FROM python:3.7-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip3 install --upgrade pip
RUN pip install psycopg2

RUN mkdir -p /sunserver
WORKDIR /sunserver

ADD . /sunserver/
RUN pip3 install -r requirements/prod.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED 1

COPY ./compose/prod/entrypoint.sh /sunserver/
ENTRYPOINT [ "/sunserver/entrypoint.sh" ]
