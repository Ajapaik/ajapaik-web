#!/bin/bash

./usr/local/bin/fix-celery.sh

cd /home/docker/ajapaik && python manage.py migrate && python manage.py loaddata licence crontabschedule periodictask \
 && python manage.py update_index && python manage.py runserver 0.0.0.0:8000
