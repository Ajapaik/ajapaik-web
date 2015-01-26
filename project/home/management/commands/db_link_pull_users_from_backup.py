from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over users from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) SELECT users.id, users.password, users.last_login, users.is_superuser, users.username, users.first_name, users.last_name, users.email, users.is_staff, users.is_active, users.date_joined FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, password, last_login,
          is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM auth_user')
          AS users(id INTEGER, password VARCHAR(128), last_login TIMESTAMP, is_superuser BOOL, username VARCHAR(30)
          ,first_name VARCHAR(30), last_name VARCHAR(30), email VARCHAR(75), is_staff BOOL, is_active BOOL, date_joined TIMESTAMP);''')