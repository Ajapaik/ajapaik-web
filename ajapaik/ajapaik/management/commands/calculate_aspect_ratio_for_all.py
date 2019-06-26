from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Photo

class Command(BaseCommand):
    help = 'Calculate aspect ratio hash for all images'

    def handle(self, *args, **options):
        photos =  Photo.objects.all().exclude(height__isnull=True).exclude(width__isnull=True)
        for photo in photos:
            photo.set_aspect_ratio()