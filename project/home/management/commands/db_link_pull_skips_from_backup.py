from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over skips from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_skip SELECT skips.id, skips.created, skips.photo_id, skips.user_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, user_id, photo_id, created FROM project_skip')
    AS skips(id integer, user_id INTEGER, photo_id integer, created TIMESTAMP);''')