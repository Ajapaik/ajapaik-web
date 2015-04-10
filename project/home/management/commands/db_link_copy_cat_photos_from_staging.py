from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Will copy over categorizer photos from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_catphoto SELECT p.id, p.title, p.description, p.image, p.created, p.modified, p.author, p.source_id, p.source_url, p.source_key FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT id, title, description, image, created, modified, author, source_id, source_url, source_key FROM project_catphoto')
    AS p(id integer, title VARCHAR(255), description VARCHAR, image VARCHAR(255), created TIMESTAMP, modified TIMESTAMP, author VARCHAR(255), source_id integer, source_url VARCHAR(255), source_key VARCHAR(255));''')