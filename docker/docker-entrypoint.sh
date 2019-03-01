#!/bin/bash

# TODO: Finish
# while ! nc -z postgres 5432; do sleep 3; done

cd /home/docker/ajapaik && python manage.py migrate && python manage.py collectstatic --noinput && \
    python manage.py compress --force && python manage.py update_index && python manage.py compilemessages && \
    #celery -A ajapaik.ajapaik beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler && \
    uwsgi --ini /home/docker/ajapaik/docker/uwsgi.ini
