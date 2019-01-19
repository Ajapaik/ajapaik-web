#!/bin/bash

cd /home/docker/ajapaik && python manage.py migrate && python manage.py loaddata licence

python manage.py runserver 0.0.0.0:8000
