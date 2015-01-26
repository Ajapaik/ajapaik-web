from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over user permissions from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO auth_user_user_permissions SELECT permissions.id, permissions.user_id, permissions.permission_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, user_id, permission_id FROM auth_user_user_permissions')
    AS permissions(id integer, user_id integer, permission_id integer);''')