from random import randint
from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = 'Refresh albums'

    def handle(self, *args, **options):
        albums = Album.objects.exclude(atype=Album.AUTO)
        for a in albums:
            if not a.lat and not a.lon and a.geotagged_photo_count_with_subalbums:
                random_index = randint(0, a.geotagged_photo_count_with_subalbums - 1)
                random_photo_with_location = a.get_geotagged_historic_photo_queryset_with_subalbums()[random_index]
                a.lat = random_photo_with_location.lat
                a.lon = random_photo_with_location.lon
            if a.photo_count_with_subalbums > 0:
                random_index = randint(0, a.photo_count_with_subalbums - 1)
            else:
                random_index = 0
            a.cover_photo_flipped = False
            try:
                random_photo = a.get_historic_photos_queryset_with_subalbums()[random_index]
                a.cover_photo = random_photo
                if random_photo and random_photo.flip:
                    a.cover_photo_flipped = random_photo.flip
            except IndexError:
                continue
            a.save()
