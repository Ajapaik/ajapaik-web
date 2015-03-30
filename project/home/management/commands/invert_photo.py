from PIL import Image, ImageOps
from django.core.management.base import BaseCommand
from project import settings
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will invert specified photo"
    args = "photo_key"

    def handle(self, *args, **options):
        try:
            photo_key = args[0]
            print photo_key
        except IndexError:
            return False
        if photo_key:
            photo = Photo.objects.get(source_key=photo_key)
            print "Found photo"
            print photo
            photo_path = settings.MEDIA_ROOT + "/" + str(photo.image)
            print photo_path
            img = Image.open(photo_path)
            inverted_grayscale_image = ImageOps.invert(img).convert('L')
            inverted_grayscale_image.save(photo_path)
            print "Inverted"
