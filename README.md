This is the open-sourced Django project code for https://ajapaik.ee/

Verified working on Python 2.7.13, instructions for installing from source (consider compiling with 
--enable-optimizations): https://tecadmin.net/install-python-2-7-on-ubuntu-and-linuxmint/

Requires installation of (at least on Ubuntu):
libxslt-dev libpq-dev python-dev libgeos-dev supervisor certbot default-jre sendmail

On your local machine cp local.py.example local.py to get a quick start.

Fix for 'django.contrib.gis.geos.error.GEOSException: Could not parse version info string "3.6.2-CAPI-1.10.2 4d2925d6"':
https://stackoverflow.com/questions/18643998/geodjango-geosexception-error

project/ajapaik/client_secrets.json needs to contain your Google credentials.

Use 'python project/manage.py createsuperuser' to make yourself a test user if need be.

Installing certbot (geolocation doesn't work without HTTPS): https://certbot.eff.org/

Requires Solr for searching. Known to work with Solr 4.10.4.

Requires OpenCV for film-still generation. Easiest installation is probably 'sudo apt install python-opencv', can try:
http://www.pyimagesearch.com/2015/06/22/install-opencv-3-0-and-python-2-7-on-ubuntu/
Last tried-working with OpenCV 3.2.0.

scikit-learn, pandas and numpy may require more involved installation than pip -r. These are currently
only required for DBSCAN geotag clustering, but may be used for various machine learning purposes in the future.

Ajapaik depends on Postgres PostGIS functionality, with a fresh-enough Postgres, installation should be easy:
http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS23UbuntuPGSQL96Apt
http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS24UbuntuPGSQL10Apt

The necessary Python modules can be installed by running the following command in the project root.
You may want to create and activate a virtualenv first:
<ul><li>pip install -r requirements.txt</li></ul>

Let Django handle the database creation, in the project root:
<ul><li>python project/manage.py migrate</li></ul>

You'll need your own local settings in project/ajapaik/settings/local.py.
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

Running tests:
source venv/bin/activate
python project/manage.py test --settings=ajapaik.settings.test --nomigrations --keepdb