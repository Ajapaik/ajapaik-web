from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over cities from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_city SELECT cities.id, cities.name, cities.lat, cities.lon FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, name, lat, lon FROM project_city')
    AS cities(id integer, name VARCHAR, lat DOUBLE PRECISION, lon DOUBLE PRECISION);''')