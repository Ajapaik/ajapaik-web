from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over difficulty feedback from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_difficultyfeedback(id, photo_id, user_profile_id, level, trustworthiness, geotag_id, created) SELECT fb.id, fb.photo_id, fb.user_profile_id, fb.level, fb.trustworthiness, fb.geotag_id, fb.created FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, photo_id , user_profile_id, level, trustworthiness, geotag_id, created FROM project_difficultyfeedback')
    AS fb(id integer, photo_id integer, user_profile_id integer, level SMALLINT, trustworthiness DOUBLE PRECISION, geotag_id INTEGER, created TIMESTAMP);''')