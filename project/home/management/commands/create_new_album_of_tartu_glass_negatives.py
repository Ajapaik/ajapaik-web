from django.core.management.base import BaseCommand
from project.home.models import AlbumPhoto


class Command(BaseCommand):
    help = 'Creates an album for original Tartu images'

    def handle(self, *args, **options):
        tartu_albumphoto_objects = AlbumPhoto.objects.filter(album_id=20)
        for each in tartu_albumphoto_objects:
            AlbumPhoto(
                album_id=219,
                photo=each.photo,
            ).save()