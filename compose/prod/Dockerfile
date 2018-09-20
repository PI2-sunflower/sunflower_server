FROM python:3.6

RUN pip3 install --upgrade pip

RUN mkdir -p /sunserver
WORKDIR /sunserver

ADD . /sunserver/
RUN pip3 install -r requirements/prod.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED 1

COPY ./compose/prod/entrypoint.sh /sunserver/
ENTRYPOINT [ "/sunserver/entrypoint.sh" ]
