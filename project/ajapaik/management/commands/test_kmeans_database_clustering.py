from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Test kmeans clustering plugin for Postgres"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''SELECT kmeans, AVG(trustworthiness), COUNT(*), array_accum(id), ST_AsText(ST_Centroid(ST_Collect(geography::GEOMETRY))) AS geom
            FROM (
              SELECT kmeans(ARRAY[ST_X(geography::GEOMETRY), ST_Y(geography::GEOMETRY)], 5) OVER () AS kmeans, id, trustworthiness, geography FROM project_geotag WHERE project_geotag.photo_id = 2663
            ) AS ksub
            GROUP BY kmeans
        ''')
        print cursor.fetchall()