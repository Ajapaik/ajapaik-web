#!/bin/bash

fix-celery.sh && cd /home/docker/ajapaik && python manage.py migrate && python manage.py collectstatic && \
    python manage.py compress --force && python manage.py update_index && \
    celery -A ajapaik.ajapaik beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler && \
    uwsgi --ini /home/docker/ajapaik/uwsgi.ini
