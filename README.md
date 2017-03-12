This is the open-sourced Django project code for https://ajapaik.ee/

The code is known to work on Python 2.7.13, Postgres 9.1 and Django 1.8.17

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
