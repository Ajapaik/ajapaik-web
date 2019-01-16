FROM python:3 AS builder

MAINTAINER Lauri Elias <lauri@ajapaik.ee>

RUN apt-get update && \
    apt-get install -y --no-install-recommends cmake build-essential

WORKDIR /home/docker/ajapaik

COPY requirements.txt .

RUN pip wheel --wheel-dir=./wheels/ -r requirements.txt

RUN pip wheel --wheel-dir=./wheels/ uwsgi

# Lightweight deployment image this time
FROM python:3-slim AS deployer

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends uwsgi nano telnet dos2unix python-opencv binutils libproj-dev \
    gdal-bin libglib2.0-0 libsm6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/docker/ajapaik

COPY --from=builder /home/docker/ajapaik/wheels/ ./wheels

COPY requirements.txt .

RUN pip install --no-index --find-links=./wheels uwsgi -r requirements.txt && rm -rf ./wheels

COPY uwsgi.ini .

COPY wsgi.py .

COPY manage.py .

COPY ajapaik ./ajapaik

COPY templates ./templates

COPY ajapaik/settings/local.py.example ajapaik/settings/local.py

COPY ajapaik-solr-schema.xml ./solr/schema.xml

COPY docker-entrypoint.sh .

RUN dos2unix docker-entrypoint.sh

# TODO: Figure out
# RUN touch ajapaik/ajapaik/client_secrets.json

EXPOSE 8000

ENTRYPOINT ["/home/docker/ajapaik/docker-entrypoint.sh"]
