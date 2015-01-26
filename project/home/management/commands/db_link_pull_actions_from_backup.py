from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over actions from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_action(id, type, related_type_id, related_id, params)SELECT actions.id, actions.type, actions.related_type_id, actions.related_id, actions.params FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, type, related_type_id, related_id, params FROM project_action')
    AS actions(id integer, type VARCHAR(255), related_type_id integer, related_id integer, params VARCHAR);''')