from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy area_id from backup base's city_id"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''UPDATE project_photo p SET area_id = bp.city_id FROM (SELECT b.city_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT city_id FROM project_photo')
    AS b(city_id);''')