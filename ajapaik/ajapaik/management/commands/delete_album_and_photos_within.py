import os

from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = 'Will delete all photos within specified album, then the album itself'
    args = 'album_id'

    def handle(self, *args, **options):
        try:
            album_id = args[0]
        except IndexError:
            return False
        if album_id:
            target = Album.objects.filter(pk=album_id).first()
            if target:
                for photo in target.photos.all():
                    if photo.image:
                        if os.path.isfile(photo.image.path):
                            # print('Want to delete file %s' % photo.image.path)
                            os.remove(photo.image.path)
                    if photo.image_unscaled:
                        if os.path.isfile(photo.image_unscaled.path):
                            # print('Want to delete file %s' % photo.image.path)
                            os.remove(photo.image_unscaled.path)
                    if photo.image_no_watermark:
                        if os.path.isfile(photo.image_no_watermark.path):
                            # print('Want to delete file %s' % photo.image.path)
                            os.remove(photo.image_no_watermark.path)
                    # print('Want to delete Photo %s' % photo.pk)
                    photo.delete()
                target.delete()
