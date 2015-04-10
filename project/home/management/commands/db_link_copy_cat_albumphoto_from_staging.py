from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Will copy over categorizer album photo relation from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_catalbum_photos SELECT p.id, p.catalbum_id, p.catphoto_id FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT id, catalbum_id, catphoto_id FROM project_catalbum_photos')
    AS p(id integer, catalbum_id integer, catphoto_id integer);''')