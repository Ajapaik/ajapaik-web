from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over devices from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_device SELECT device.id, device.camera_make, device.camera_model, device.lens_make, device.lens_model, device.software FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT id, camera_make, camera_model, lens_make, lens_model, software FROM project_device')
    AS device(id integer, camera_make VARCHAR(255), camera_model VARCHAR(255), lens_make VARCHAR(255), lens_model VARCHAR(255), software VARCHAR(255));''')