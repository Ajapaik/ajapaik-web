from django.core.management.base import BaseCommand
from django.db import connection
from project.home.models import Photo


class Command(BaseCommand):
    help = "Restore muis_id from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''SELECT p.id, p.muis_id FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, muis_id FROM project_photo WHERE muis_id IS NOT NULL')
    AS p(id integer, muis_id VARCHAR(100));''')
        result = cursor.fetchall()
        for each in result:
            p = Photo.objects.filter(pk=each[0]).first()
            if p:
                p.muis_id = each[1]
                p.light_save()