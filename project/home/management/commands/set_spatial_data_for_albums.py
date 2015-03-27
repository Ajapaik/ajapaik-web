from django.core.management.base import BaseCommand
from project.home.models import Album
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Set geography field for albums"

    def handle(self, *args, **options):
        albums = Album.objects.filter(geography__isnull=True)
        for a in albums:
            a.geography = Point(x=float(a.lat), y=float(a.lon), srid=4326)
            a.save()