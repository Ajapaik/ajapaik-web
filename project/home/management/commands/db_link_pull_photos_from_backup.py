from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over photos from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_photo SELECT p.id, p.image, p.image_unscaled, p.flip, p.date, p.date_text, p.description, p.level, p.guess_level, p.lat, p.lon, p.bounding_circle_radius, p.azimuth, p.confidence, p.azimuth_confidence, p.source_key, p.source_url, p.created, p.modified, p.cam_scale_factor, p.cam_yaw, p.cam_pitch, p.cam_roll, p.city_id, p.device_id, p.rephoto_of_id, p.source_id, p.user_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, image, date, description, level, guess_level, source_key, source_id, rephoto_of_id, created, modified, date_text, user_id, lat, lon, confidence, city_id, cam_scale_factor, cam_yaw, cam_pitch, cam_roll, source_url, device_id, image_unscaled, bounding_circle_radius, azimuth, azimuth_confidence, flip FROM project_photo')
    AS p(id integer, image VARCHAR(100), date DATE, description VARCHAR, level SMALLINT, guess_level DOUBLE PRECISION, source_key VARCHAR(100), source_id integer, rephoto_of_id integer, created TIMESTAMP, modified TIMESTAMP, date_text VARCHAR(100), user_id INTEGER, lat DOUBLE PRECISION, lon DOUBLE PRECISION, confidence DOUBLE PRECISION, city_id INT, cam_scale_factor DOUBLE PRECISION, cam_yaw DOUBLE PRECISION, cam_pitch DOUBLE PRECISION, cam_roll DOUBLE PRECISION, source_url VARCHAR(1023), device_id integer, image_unscaled VARCHAR(100), bounding_circle_radius DOUBLE PRECISION, azimuth DOUBLE PRECISION, azimuth_confidence DOUBLE PRECISION, flip BOOL);''')