from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over geotags from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_geotag (id, lat, lon, type, created, modified, user_id, photo_id, is_correct, score, trustworthiness, azimuth, zoom_level, azimuth_score, origin) SELECT gt.id, gt.lat, gt.lon, gt.type, gt.created, gt.modified, gt.user_id, gt.photo_id, gt.is_correct, gt.score, gt.trustworthiness, gt.azimuth, gt.zoom_level, gt.azimuth_score, 0 FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, lat, lon, type, created, modified, user_id, photo_id, is_correct, score, trustworthiness, azimuth, zoom_level, azimuth_score FROM project_geotag')
    AS gt(id integer, lat DOUBLE PRECISION, lon DOUBLE PRECISION, type SMALLINT, created TIMESTAMP, modified TIMESTAMP, user_id integer, photo_id integer, is_correct BOOL, score SMALLINT, trustworthiness DOUBLE PRECISION, azimuth DOUBLE PRECISION, zoom_level INTEGER, azimuth_score SMALLINT);''')