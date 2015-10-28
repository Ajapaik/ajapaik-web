from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success
from project.ajapaik.models import Photo
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = "Set geography field for photos"

    @commit_on_success
    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False)
        for p in photos:
            print p.id
            p.geography = Point(x=float(p.lon), y=float(p.lat), srid=4326)
            p.light_save()