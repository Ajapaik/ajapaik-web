from django.core.management.base import BaseCommand
from project.home.models import City, Album

class Command(BaseCommand):
    help = "Convert the contents of the current city table into albums"

    def handle(self, *args, **options):
        cities = City.objects.all()
        for c in cities:
            new_album = Album()
            new_album.name = c.name
            new_album.lat = c.lat
            new_album.lon = c.lon
            new_album.atype = Album.FRONTPAGE
            new_album.is_public = True
            new_album.save()