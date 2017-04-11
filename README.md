This is the open-sourced Django project code for https://ajapaik.ee/

Verified working on Python 2.7.13, instructions for installing from source (consider compiling with --enable-optimizations):
https://tecadmin.net/install-python-2-7-on-ubuntu-and-linuxmint/

The code is known to work on Python 2.7.12, Postgres 8.4 and Django 1.7.11

Ajapaik depends on Postgres PostGIS functionality, on Postgres 8.4 the installation goes as follows:
<ol>
  <li>createlang plpgsql yourdatabase</li>
  <li>cd /usr/share/postgresql/8.4/contrib/postgis-1.5 (on Debian Squeeze)</li>
  <li>sudo su - postgres</li>
  <li>psql -d yourdatabase -f postgis.sql</li>
  <li>psql -d yourdatabase -f spatial_ref_sys.sql</li>
</ol>

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
