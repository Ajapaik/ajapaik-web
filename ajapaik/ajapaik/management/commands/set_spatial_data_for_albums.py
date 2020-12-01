from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = "Set geography field for albums"

    def handle(self, *args, **options):
        albums = Album.objects.all()
        for a in albums:
            if a.lat and a.lon:
                # print a.id
                a.geography = Point(x=float(a.lon), y=float(a.lat), srid=4326)
                a.light_save()
