FROM laurielias/python-3.6-dlib:latest AS builder
# dlib takes awful long to install

# TODO: Consider gcr.io/distroless/python3:latest?

MAINTAINER Lauri Elias <lauri@ajapaik.ee>

RUN apt-get update && \
    apt-get install -y --fix-missing cmake build-essential gfortran git wget curl graphicsmagick \
    libgraphicsmagick1-dev libatlas-dev libavcodec-dev libavformat-dev libgtk2.0-dev libjpeg-dev liblapack-dev \
    libswscale-dev pkg-config python3-dev python3-numpy software-properties-common zip

WORKDIR /home/docker/ajapaik

COPY requirements.txt .

RUN pip wheel --wheel-dir=./wheels/ uwsgi

RUN pip wheel --wheel-dir=./wheels/ -r requirements.txt

# Lightweight deployment image this time
FROM python:3.6-slim AS deployer

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends uwsgi nano telnet python-opencv binutils libproj-dev \
    gdal-bin libglib2.0-0 libsm6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/docker/ajapaik

COPY --from=builder /home/docker/ajapaik/wheels ./wheels

COPY requirements.txt uwsgi.ini wsgi.py manage.py ./

RUN pip install --no-index --find-links=./wheels uwsgi -r requirements.txt && rm -rf ./wheels

COPY ajapaik ./ajapaik

COPY templates ./templates

COPY ajapaik/settings/local.py.example ajapaik/settings/local.py

COPY solr ./solr

COPY docker-entrypoint.sh docker-entrypoint-dev.sh fix-celery.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint-dev.sh /usr/local/bin/fix-celery.sh

# TODO: Figure out
# RUN touch ajapaik/ajapaik/client_secrets.json

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
