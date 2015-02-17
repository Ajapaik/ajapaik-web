from django.core.management.base import BaseCommand
from project.home.models import GeoTag
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Set geography field for geotags"

    def handle(self, *args, **options):
        geotags = GeoTag.objects.filter(geography__isnull=True)
        for g in geotags:
            g.geography = Point(x=float(self.lon), y=float(self.lat), srid=4326)
            g.save()