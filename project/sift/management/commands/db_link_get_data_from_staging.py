from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Take data since friday from staging (little config mishap)"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_cattagphoto SELECT value, created, modified, photo_id, tag_id, profile_id, album_id, source FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT value, created, modified, photo_id, tag_id, profile_id, album_id, source FROM project_cattagphoto WHERE created > "2015-09-04"')
          AS p(value INT, created TIMESTAMP, modified TIMESTAMP, photo_id INT, tag_id INT, profile_id INT, album_id INT, source VARCHAR(3));''')
        cursor.execute('''INSERT INTO project_catuserfavorite SELECT created, modified, album_id, photo_id, profile_id FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT created, modified, album_id, photo_id, profile_id FROM project_catuserfavorite WHERE created > "2015-09-04"')
          AS p(created TIMESTAMP, modified TIMESTAMP, album_id INT, photo_id INT, profile_id INT);''')