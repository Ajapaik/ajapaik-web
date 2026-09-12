from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Set geography field for photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False)
        for p in photos:
            p.geography = Point(x=float(p.lon), y=float(p.lat), srid=4326)
            p.light_save()
