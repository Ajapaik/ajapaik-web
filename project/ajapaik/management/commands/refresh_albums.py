from random import randint
from django.core.management.base import BaseCommand
from django.db.models import Count
from project.ajapaik.models import Album


class Command(BaseCommand):
    help = "Refresh albums"

    def handle(self, *args, **options):
        albums = Album.objects.exclude(atype=Album.AUTO).annotate(photo_count=Count('photos'))
        for a in albums:
            if not a.lat and not a.lon:
                random_photo_with_location = a.get_historic_photos_queryset_with_subalbums()\
                    .filter(lat__isnull=False, lon__isnull=False).order_by('?').first()
                a.lat = random_photo_with_location.lat
                a.lon = random_photo_with_location.lon
            if a.photo_count > 0:
                random_index = randint(0, a.photo_count - 1)
            else:
                random_index = 0
            a.cover_photo_flipped = False
            try:
                random_photo = a.photos.filter(rephoto_of__isnull=True)[random_index]
                a.cover_photo = random_photo
                if random_photo.flip:
                    a.cover_photo_flipped = random_photo.flip
            except IndexError:
                for sa in a.subalbums.exclude(atype=Album.AUTO).annotate(photo_count=Count('photos')):
                    if sa.photo_count > 0:
                        random_index = randint(0, sa.photo_count - 1)
                        try:
                            random_photo = sa.photos.filter(rephoto_of__isnull=True)[random_index]
                            a.cover_photo = random_photo
                            if random_photo.flip:
                                a.cover_photo_flipped = random_photo.flip
                            break
                        except IndexError:
                            continue
            a.save()