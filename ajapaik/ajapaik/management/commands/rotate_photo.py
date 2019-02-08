from PIL import Image
from django.core.management.base import BaseCommand
from ajapaik import settings
from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will rotate specified photo specified degrees"
    args = "photo_id, degrees"

    def handle(self, *args, **options):
        photo_id = args[0]
        degrees = int(args[1])
        photo = Photo.objects.filter(pk=photo_id).first()
        photo_path = settings.MEDIA_ROOT + "/" + str(photo.image)
        img = Image.open(photo_path)
        rot = img.rotate(degrees, expand=1)
        rot.save(photo_path)
        if photo.rotated:
            photo.rotated += degrees
        else:
            photo.rotated = degrees
        photo.save()