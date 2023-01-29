#!/bin/bash

while ! nc -z db 5432; do sleep 3; done

if [ ! -f /home/docker/ajapaik/ajapaik/settings/local.py ]; then
    cp /home/docker/ajapaik/ajapaik/settings/local.py.example /home/docker/ajapaik/ajapaik/settings/local.py
fi

pip install -r requirements.txt

cd /home/docker/ajapaik && python manage.py loaddata licence object_detection_models \
  && python manage.py update_index && python manage.py compilemessages && \
  python manage.py runserver 0.0.0.0:8000
