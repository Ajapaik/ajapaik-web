#!/bin/bash

cd /home/docker/ajapaik && python manage.py migrate && python manage.py loaddata licence \
 crontabschedule periodictask && python manage.py update_index && python manage.py compilemessages && \
 #celery -A ajapaik.ajapaik beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler && \
 python manage.py runserver 0.0.0.0:8000
