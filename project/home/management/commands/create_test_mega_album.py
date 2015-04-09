from django.core.management.base import BaseCommand
from project.home.models import Photo, Album, AlbumPhoto


class Command(BaseCommand):
    help = "Create 5000 photo album"

    def handle(self, *args, **options):
        album = Album.objects.get(pk=372)
        for each in Photo.objects.filter()[:5000]:
            AlbumPhoto(
                album=album,
                photo=each,
            ).save()