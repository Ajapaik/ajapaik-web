from PIL import Image
from django.core.management.base import BaseCommand
from sorl.thumbnail import delete

from project.ajapaik import settings
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Flip all photos that have flip == true'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(flip=True, rephoto_of__isnull=True)
        for p in photos:
            print p.id
            photo_path = settings.MEDIA_ROOT + "/" + str(p.image)
            img = Image.open(photo_path)
            flipped_image = img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_image.save(photo_path)
            delete(p.image, delete_file=False)