FROM debian:buster-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        freetds-dev \
        build-essential \
        python3-tk \
        python3-matplotlib

RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

RUN pip3 install --upgrade pip

RUN mkdir -p /sunserver
WORKDIR /sunserver

COPY requirements /sunserver/requirements
RUN pip3 install -r requirements/dev.txt
RUN pip3 install --extra-index-url https://test.pypi.org/simple/ sunflower-low-level --no-cache-dir 
ADD . /sunserver/
RUN chmod +x compose/entrypoint.sh

ENV PYTHONUNBUFFERED 1
