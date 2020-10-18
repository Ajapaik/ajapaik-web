from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Photo

class Command(BaseCommand):
    help = 'Calculate perceptual hash for images and then find similar images from all added images'

    def handle(self, *args, **options):
        newPhotos =  Photo.objects.filter(perceptual_hash__isnull=True, rephoto_of__isnull=True, back_of__isnull=True)
        for newPhoto in newPhotos:
            try:
                newPhoto.find_similar()
            except Exception:
                continue
