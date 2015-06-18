from PIL import Image
from django.core.management.base import BaseCommand
from project import settings
from project.home.models import CatPhoto


class Command(BaseCommand):
    help = "Will rotate specified cat photo specified degrees"
    args = "photo_id, degrees"

    def handle(self, *args, **options):
        photo_id = args[0]
        degrees = int(args[1])
        photo = CatPhoto.objects.filter(pk=photo_id).first()
        photo_path = settings.MEDIA_ROOT + "/" + str(photo.image)
        img = Image.open(photo_path)
        rot = img.rotate(degrees, expand=1)
        rot.save(photo_path)
        if photo.rotated:
            photo.rotated += degrees
        else:
            photo.rotated = degrees
        photo.save()