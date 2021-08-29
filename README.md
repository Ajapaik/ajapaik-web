![Python application](https://github.com/Ajapaik/ajapaik-web/workflows/Python%20application/badge.svg)
[![codecov](https://codecov.io/gh/Ajapaik/ajapaik-web/branch/master/graph/badge.svg)](https://codecov.io/gh/Ajapaik/ajapaik-web)

## [Join Ajapaik Slack](http://bit.ly/join-Ajapaik-Slack)!
This is the open-sourced Django project code for https://ajapaik.ee/

## Running locally
```bash
docker pull laurielias/ajapaik-web:python-3.6-latest
docker-compose up
```

## Build it yourself and launch
python-3.6-dlib is just python:3.6 with dlib and its dependencies installed. (compiling takes 10+ minutes otherwise)
```bash
docker pull laurielias/python-3.6-dlib
docker-compose up --build
```

## Multi-Device Testing
<a href="https://www.browserstack.com" target="_blank"><img src="ajapaik/ajapaik/static/images/BrowserStack-logo.svg" alt="BrowserStack" width="320"></a>

We use [BrowserStack](https://www.browserstack.com) to test on a variety of devices and operating systems.


## Restore data from a dump
```SQL
CREATE DATABASE rephoto_production_20190511;
CREATE USER rephoto WITH ENCRYPTED PASSWORD '';
GRANT ALL PRIVILEGES ON DATABASE rephoto_production_20190511 TO rephoto;
```
```bash
psql -d rephoto_production_20190511 -U postgres < rephoto_20210426.schema.dump
# Data only, no integrity checks while loading it in, no privileges
pg_restore rephoto_20210426.sql -d rephoto_production_20190511 -a -x --disable-triggers -U postgres
``` 

## Push new image
```bash
docker push laurielias/ajapaik-web:python-3.6-latest
```

## Debug the container
If need be override the entrypoint in docker-compose.yml to tail -f /dev/null or the like. 
(in case the current entrypoint crashes, for example)
```bash
docker exec -it ajapaik bash
```

## Starting with a fresh DB, add a Django superuser
In the container:
```bash
python manage.py createsuperuser
```

## Deploy on our server - currently still using old school supervisord + uwsgis
Make sure you have local.py (mostly secret Django settings) and client_secrets.json (Google credentials) in your 
project root. They will be mounted into the container on startup. Make sure the nginx on the host knows how to
proxy traffic to this container. Also symlink the media directory (the one with all the photos) into your project root,
same for the Postgres data directory. Push/pull images again to update.
```bash
docker-compose up -f docker-compose.dev.yml
```

## Update Juks' Vanalinnad data
```bash
wget -r --no-parent -A empty.json,layers.xml http://vanalinnad.mooo.com/vector/places/
wget -r --no-parent -A *.jpg http://vanalinnad.mooo.com/raster/places/
```

## Misc. running instructions

On your local machine cp local.py.example local.py to get a quick start.

Fix for 'django.contrib.gis.geos.error.GEOSException: Could not parse version info string "3.6.2-CAPI-1.10.2 4d2925d6"':
https://stackoverflow.com/questions/18643998/geodjango-geosexception-error

Installing Postgres:
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04

May be of help:
ALTER USER ajapaik WITH PASSWORD 'seekrit';
GRANT ALL PRIVILEGES ON DATABASE ajapaik TO ajapaik;

Ajapaik depends on Postgres PostGIS functionality, with a fresh-enough Postgres, installation should be easy:
http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS23UbuntuPGSQL96Apt
http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS24UbuntuPGSQL10Apt

You'll need your own local settings in ajapaik/settings/local.py.
You should at least override or specify the following keys:
<ul>
  <li>ADMINS</li>
  <li>MANAGERS</li>
  <li>DATABASES</li>
  <li>SECRET_KEY</li>
  <li>LOGGING</li>
  <li>GOOGLE_API_KEY</li>
  <li>GOOGLE_MAPS_API_KEY</li>
  <li>GOOGLE_ANALYTICS_KEY</li>
  <li>ALLOWED_HOSTS</li>
</ul>

## Running tests

```bash
source venv/bin/activate
python manage.py test --settings=ajapaik.settings.test --nomigrations --keepdb
```

## To-do list

- TODO: command for regular stats exports
- TODO: fix core dump https://github.com/ageitgey/face_recognition/issues/11
- TODO: automate stats queries or at least document them better (should be possible with a Google Sheets API key?)
- TODO: try if integrating Solr tighter will help search (the current solution where everything that matches 'Tartu' is retrieved into an array of IDs no longer performs)
- TODO: implement this answer for keeps https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
- TODO: automate regular DB, media/uploads, media/videos backups
- TODO: fix # noqa as much as possible (some Django quirks will always annoy flake8 though)
- TODO: replace face_recognition with something else since it requires the horrendous dlib
