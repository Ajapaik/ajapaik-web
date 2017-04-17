This is the open-sourced Django project code for https://ajapaik.ee/

Verified working on Python 2.7.13, instructions for installing from source (consider compiling with 
--enable-optimizations): https://tecadmin.net/install-python-2-7-on-ubuntu-and-linuxmint/

Requires libxslt-dev, libpq-dev, python-dev, libgeos-dev.

Requires Solr for searching. Known to work with 4.10.4.

Requires OpenCV for film-still generation. Easiest installation is probably:
1) sudo apt install libopencv-dev python-opencv
2) cp /usr/lib/pymodules/python2.7/cv* $VIRTUAL_ENV/lib/python2.7/site-packages/
3) If 1) and 2) don't work, installing from source:
https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313

scikit-learn, pandas and numpy may require more involved installation than pip -r. These are currently
only required for DBSCAN geotag clustering, but may be used for various machine learning purposes in the future.

Ajapaik depends on Postgres PostGIS functionality, with a fresh-enough Postgres installation should be easy:
http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS23UbuntuPGSQL96Apt

The necessary Python modules can be installed by running the following command in the project root. You may want to create a virtualenv first:
<ul><li>pip install -r requirements.txt</li></ul>

Let Django handle the database creation, in the project root:
<ul><li>python project/manage.py migrate</li></ul>

You'll need your own local settings in project/ajapaik/settings/local.py. You should at least override or specify the following keys:
<ul>
  <li>ADMINS</li>
  <li>MANAGERS</li>
  <li>DATABASES</li>
  <li>SECRET_KEY</li>
  <li>GOOGLE_MAPS_API_KEY</li>
  <li>GOOGLE_ANALYTICS_KEY</li>
  <li>ALLOWED_HOSTS</li>
</ul>
