#!/bin/bash

cd /home/docker/ajapaik && python manage.py migrate && python manage.py collectstatic && \
    python manage.py compress --force

uwsgi --ini /home/docker/ajapaik/uwsgi.ini
