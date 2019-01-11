FROM python:2 AS builder

MAINTAINER Lauri Elias <lauri@ajapaik.ee>

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends cmake build-essential

WORKDIR /home/docker/ajapaik

COPY . .

RUN pip install --upgrade pip && pip install wheel uwsgi && pip install -e .

RUN pip wheel --wheel-dir=./wheels/ project

RUN pip wheel --wheel-dir=./wheels/ uwsgi

# Lightweight deployment image this time
FROM python:2-slim AS deployer

WORKDIR /home/docker/ajapaik

COPY --from=builder /home/docker/ajapaik/wheels/ ./wheels

COPY --from=builder /home/docker/ajapaik/uwsgi.ini .

RUN pip install --no-index --find-links=./wheels project uwsgi

EXPOSE 8000

ENTRYPOINT ["uwsgi"]

CMD ["/home/docker/ajapaik/uwsgi.ini"]