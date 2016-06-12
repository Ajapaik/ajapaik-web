from _csv import reader

from django.core.management import BaseCommand
from django.utils.translation import activate

from project.ajapaik.models import AlbumPhoto, Photo
from project.ajapaik.settings import ABSOLUTE_PROJECT_ROOT


class Command(BaseCommand):
    help = "Fix for missing author fields for a Norwegian album"

    def handle(self, *args, **options):
        activate('no')
        album_photo_ids = AlbumPhoto.objects.filter(album_id=8334).values_list('photo_id', flat=True)
        photos = Photo.objects.filter(pk__in=album_photo_ids)
        f = open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/riksantikvaren_bergen.csv', 'r')
        header_row = None
        photos_metadata = {}
        for row in reader(f, delimiter=';'):
            if not header_row:
                header_row = row
                continue
            row = dict(zip(header_row, row))
            photos_metadata[row.get('number').split('.')[0]] = row
        for p in photos:
            p.author = photos_metadata[p.source_key].get('author')
            p.light_save()