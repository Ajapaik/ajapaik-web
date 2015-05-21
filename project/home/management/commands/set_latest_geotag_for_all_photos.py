from django.core.management.base import BaseCommand
from project.home.models import Photo, GeoTag


class Command(BaseCommand):
    help = "Set latest geotag for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        for p in photos:
            print p.id
            latest_geotag = GeoTag.objects.filter(photo=p).order_by('-created').first()
            if latest_geotag:
                p.latest_geotag = latest_geotag.created