#!/bin/bash

# TODO: Finish
# while ! nc -z postgres 5432; do sleep 3; done

cd /home/docker/ajapaik && python manage.py migrate --noinput && python manage.py collectstatic --noinput && \
    python manage.py compress --force && python manage.py update_index && python manage.py compilemessages && \
    uwsgi --ini /home/docker/ajapaik/docker/uwsgi.ini
