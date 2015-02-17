from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over licences from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_licence(id, name, url, image_url) SELECT licences.id, licences.name, licences.url, licences.image_url FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT id, name, url, image_url FROM project_licence')
    AS licences(id integer, name VARCHAR(255), url VARCHAR, image_url VARCHAR);''')