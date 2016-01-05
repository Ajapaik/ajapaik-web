from PIL import Image, ImageOps
from django.core.management.base import BaseCommand
from project.ajapaik import settings
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will invert specified photo"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
            print photo_id
        except IndexError:
            return False
        if photo_id:
            photo = Photo.objects.get(pk=photo_id)
            print "Found photo"
            print photo
            photo_path = settings.MEDIA_ROOT + "/" + str(photo.image)
            print photo_path
            img = Image.open(photo_path)
            inverted_grayscale_image = ImageOps.invert(img).convert('L')
            inverted_grayscale_image.save(photo_path)
            print "Inverted"
            photo.invert = True
            photo.save()