from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Will copy over categorizer photos from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_catalbum SELECT p.id, p.title, p.subtitle, p.image, p.created, p.modified FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT id, title, subtitle, image, created, modified FROM project_catalbum')
    AS p(id integer, title VARCHAR(255), subtitle VARCHAR(255), image VARCHAR(255), created TIMESTAMP, modified TIMESTAMP);''')