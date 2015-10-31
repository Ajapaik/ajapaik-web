from django.core.management.base import BaseCommand
from project.ajapaik.models import Album


class Command(BaseCommand):
    help = 'Deletes photos assigned to junk album'
    args = 'album_id'

    def handle(self, *args, **options):
        album_id = args[0]
        album = Album.objects.get(pk=album_id)
        for p in album.photos.all():
            print p.pk
            p.image.delete()
            p.delete()
