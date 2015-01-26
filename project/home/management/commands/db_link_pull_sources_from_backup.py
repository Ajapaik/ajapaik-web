from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over sources from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_source SELECT source.id, source.name, source.description, source.created, source.modified FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, name, created, modified, description FROM project_source')
    AS source(id integer, name VARCHAR(255), created TIMESTAMP, modified TIMESTAMP, description VARCHAR);''')