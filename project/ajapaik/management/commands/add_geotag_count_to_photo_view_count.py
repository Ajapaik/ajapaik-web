from django.core.management.base import BaseCommand
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Adds geotag count to all photos\' view count, since they must have been seen in order to be geotagged'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        for p in photos:
            p.view_count += p.geotags.count()
            p.light_save()