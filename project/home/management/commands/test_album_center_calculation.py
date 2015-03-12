from django.core.management.base import BaseCommand
from project.home.models import Album


class Command(BaseCommand):
    help = "Test if we can calculate a center for an album"
    args = "album_id"

    def handle(self, *args, **options):
        album_id = args[0]
        album = Album.objects.get(pk=album_id)
        album_photos = album.photos.all()
        lat_sum = 0
        lon_sum = 0
        lat_lon_count = 0
        for ap in album_photos:
            if ap.lat and ap.lon:
                lat_sum += ap.lat
                lon_sum += ap.lon
                lat_lon_count += 1
        print lat_sum / lat_lon_count
        print lon_sum / lat_lon_count