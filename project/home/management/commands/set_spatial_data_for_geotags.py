from django.core.management.base import BaseCommand
from project.home.models import GeoTag
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Set geography field for geotags"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
        except:
            photo_id = None
        if photo_id:
            geotags = GeoTag.objects.filter(geography__isnull=True, photo_id=photo_id)
        else:
            geotags = GeoTag.objects.filter(geography__isnull=True)
        for g in geotags:
            try:
                g.geography = Point(x=float(g.lat), y=float(g.lon), srid=4326)
                g.save()
            except:
                continue