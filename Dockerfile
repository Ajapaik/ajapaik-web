FROM python:3 AS builder

MAINTAINER Lauri Elias <lauri@ajapaik.ee>

RUN apt-get update && \
    apt-get install -y --no-install-recommends cmake build-essential

WORKDIR /home/docker/ajapaik

COPY . .

# RUN cp ajapaik/settings/local.py.example ajapaik/settings/local.py

RUN pip install wheel uwsgi && \
    pip install -e .

RUN pip wheel --wheel-dir=./wheels/ .

RUN pip wheel --wheel-dir=./wheels/ uwsgi

# Lightweight deployment image this time
FROM python:3-slim AS deployer

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends uwsgi nano telnet memcached binutils libproj-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/docker/ajapaik

COPY --from=builder /home/docker/ajapaik/wheels/ ./wheels

COPY --from=builder /home/docker/ajapaik/uwsgi.ini .

COPY --from=builder /home/docker/ajapaik/wsgi.py .

RUN pip install --no-index --find-links=./wheels ajapaik uwsgi

EXPOSE 8000

ENTRYPOINT ["uwsgi"]

CMD ["/home/docker/ajapaik/uwsgi.ini"]