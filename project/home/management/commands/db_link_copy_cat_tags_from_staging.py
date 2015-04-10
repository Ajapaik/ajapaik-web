from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Will copy over categorizer tags from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_cattag SELECT p.id, p.name, p.level, p.active FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT id, name, level, active FROM project_cattag')
    AS p(id integer, name VARCHAR(255), level SMALLINT, active BOOL);''')