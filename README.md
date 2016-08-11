This is the open-sourced Django project code for http://ajapaik.ee/

The code is known to work on Python 2.7.8, Postgres 8.4 and Django 1.7.2

Ajapaik depends on Postgres PostGIS functionality, on Postgres 8.4 the installation goes as follows:
<ol>
  <li>createlang plpgsql yourdatabase</li>
  <li>cd /usr/share/postgresql/8.4/contrib/postgis-1.5 (on Debian Squeeze)</li>
  <li>sudo su - postgres</li>
  <li>psql -d yourdatabase -f postgis.sql</li>
  <li>psql -d yourdatabase -f spatial_ref_sys.sql</li>
</ol>

A currently experimental feature uses a Postgres extension named kmeans and you may need to install it. (http://pgxn.org/dist/kmeans/) You can hopefully skip the next 2 sets of instructions, but if you start getting errors, here they are anyway:
<ol>
  <li>wget http://api.pgxn.org/dist/kmeans/1.1.0/kmeans-1.1.0.zip</li>
  <li>unzip kmeans-1.1.0.zip</li>
  <li>cd kmeans-1.1.0/</li>
  <li>export USE_PGXS=1</li>
  <li>make</li>
  <li>make install</li>
  <li>sudo su -postgres</li>
  <li>psql -f /usr/share/postgresql/8.4/contrib/kmeans.sql -d yourdatabase</li>
</ol>

A utility function for the aforementioned feature:
<ul>
  <li>In yourdatabase: CREATE AGGREGATE array_accum (anyelement)
  (
      sfunc = array_append,
      stype = anyarray,
      initcond = '{}'
  );
  </li>
</ul>

The necessary Python modules can be installed by running the following command in the project root. You may want to create a virtualenv first:
<ul><li>pip install -r requirements.txt</li></ul>

Let Django handle the database creation, in the project root:
<ul><li>python project/manage.py migrate</li></ul>

You'll need your own local settings in project/settings/local.py. You should at least override or specify the following keys:
<ul>
  <li>ADMINS</li>
  <li>MANAGERS</li>
  <li>DATABASES</li>
  <li>SECRET_KEY</li>
  <li>GOOGLE_MAPS_API_KEY</li>
  <li>GOOGLE_ANALYTICS_KEY</li>
  <li>ALLOWED_HOSTS</li>
</ul>
