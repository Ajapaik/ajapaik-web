from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = "Will run set_calculated_fields and save for one or every album"
    args = "album_id"

    def handle(self, *args, **options):
        try:
            album_id = args[0]
        except IndexError:
            album_id = None
        if album_id:
            album = Album.objects.get(pk=album_id)
            album.set_calculated_fields()
            album.save()
        else:
            for album in Album.objects.all():
                album.set_calculated_fields()
                album.save()
