from PIL import Image
from django.core.management.base import BaseCommand
from project.sift.models import CatPhoto
from project.sift.settings import MEDIA_ROOT


class Command(BaseCommand):
    help = "Will rotate specified Sift photo specified degrees"
    args = "photo_id, degrees"

    def handle(self, *args, **options):
        photo_id = int(args[0])
        degrees = int(args[1])
        photo = CatPhoto.objects.filter(pk=photo_id).first()
        photo_path = MEDIA_ROOT + "/" + str(photo.image)
        img = Image.open(photo_path)
        rot = img.rotate(degrees, expand=1)
        rot.save(photo_path)
        if photo.rotated:
            photo.rotated += degrees
        else:
            photo.rotated = degrees
        photo.save()
