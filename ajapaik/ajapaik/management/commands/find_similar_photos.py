from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Calculate perceptual hash for images and then find similar images from all newly added images (w/o hash)'

    def handle(self, *args, **options):
        new_photos = Photo.objects.filter(perceptual_hash__isnull=True, rephoto_of__isnull=True, back_of__isnull=True)
        for newPhoto in new_photos:
            try:
                newPhoto.find_similar()
            except Exception:
                continue
