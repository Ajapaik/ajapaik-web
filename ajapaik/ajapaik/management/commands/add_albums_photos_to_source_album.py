from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import AlbumPhoto, Photo


class Command(BaseCommand):
    help = "Adds all photos of albums to the corresponding source albums"

    def add_arguments(self, parser):
        parser.add_argument(
            'album_ids', nargs='+', type=int, help='Imported album ids, where there are photos which are not in source album'
        )

    def handle(self, *args, **options):
        if options['album_ids']:
            album_photos = AlbumPhoto.objects.filter(album_id__in=options['album_ids'])
            for album_photo in album_photos:
                album_photo.photo.add_to_source_album()