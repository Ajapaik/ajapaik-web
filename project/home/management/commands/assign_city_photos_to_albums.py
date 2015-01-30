from django.core.management.base import BaseCommand
from project.home.models import Album, Photo, AlbumPhoto


class Command(BaseCommand):
    help = "Photos will be assigned a city album based on their current city"

    def handle(self, *args, **options):
        albums = Album.objects.all()
        for a in albums:
            photos_belonging_to_current_album = Photo.objects.filter(city_id=a.id)
            for p in photos_belonging_to_current_album:
                ap = AlbumPhoto()
                ap.album = a
                ap.photo = p
                ap.save()