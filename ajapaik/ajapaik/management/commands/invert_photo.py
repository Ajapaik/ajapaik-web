from PIL import Image, ImageOps
from django.core.management.base import BaseCommand

from ajapaik import settings
from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will invert specified photo"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
        except IndexError:
            return False
        if photo_id:
            photo = Photo.objects.get(pk=photo_id)
            photo_path = f'{settings.MEDIA_ROOT}/{str(photo.image)}'
            img = Image.open(photo_path)
            inverted_grayscale_image = ImageOps.invert(img).convert('L')
            inverted_grayscale_image.save(photo_path)
            photo.invert = True
            photo.save()
