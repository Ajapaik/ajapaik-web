from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over django sessions from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO django_session SELECT sessions.session_key, sessions.session_data, sessions.expire_date FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT session_key, session_data, expire_date FROM django_session')
    AS sessions(session_key VARCHAR(40), session_data VARCHAR, expire_date TIMESTAMP);''')