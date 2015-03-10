from django.core.management.base import BaseCommand
from project.home.models import Area, Album, Photo, AlbumPhoto


class Command(BaseCommand):
    help = 'Makes albums from existing areas'

    def handle(self, *args, **options):
        areas = Area.objects.all()
        for a in areas:
            album = Album(
                name=a.name,
                atype=Album.CURATED,
                is_public=True
            )
            album.save()
            area_photos = Photo.objects.filter(area_id=a.id)
            for ap in area_photos:
                album_photo = AlbumPhoto(
                    album=album,
                    photo=ap
                )
                album_photo.save()