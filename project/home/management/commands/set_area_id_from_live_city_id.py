from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy area_id from backup bases city_id"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''UPDATE project_photo SET area_id = b.city_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, city_id FROM project_photo') AS b(id integer, city_id integer) WHERE project_photo.id = b.id AND b.city_id < 14''')