from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Calculate aspect ratio hash for all images'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(source_url__contains='www.muis.ee/museaal').filter(id=1723)
        for photo in photos:
            photo.set_calculated_fields()
            photo.save()
