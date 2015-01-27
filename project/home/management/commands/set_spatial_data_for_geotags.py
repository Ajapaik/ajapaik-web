from django.core.management.base import BaseCommand
from project.home.models import GeoTag
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Set geography field for geotags"
    args = "photo_id"

    def handle(self, *args, **options):
        photo_id = args[0]
        geotags = GeoTag.objects.filter(photo_id=photo_id)
        for g in geotags:
            g.geography = Point(float(g.lat), float(g.lon))
            g.save()