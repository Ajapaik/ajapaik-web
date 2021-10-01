from random import randint
import time

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = 'Refresh albums'

    def handle(self, *args, **options):
        albums = Album.objects.exclude(atype__in=[Album.AUTO, Album.FAVORITES])
        for a in albums:
            historic_photo_qs = a.get_historic_photos_queryset_with_subalbums()
            if not historic_photo_qs.exists():
                continue

            geotagged_photo_qs = a.get_geotagged_historic_photo_queryset_with_subalbums()
            a.photo_count_with_subalbums = historic_photo_qs.count()
            a.geotagged_photo_count_with_subalbums = geotagged_photo_qs.count()
            a.rephoto_count_with_subalbums = a.get_rephotos_queryset_with_subalbums().count()
            a.comments_count_with_subalbums = a.get_comment_count_with_subalbums()
            a.similar_photo_count_with_subalbums = a.get_similar_photo_count_with_subalbums()
            a.confirmed_similar_photo_count_with_subalbums = a.get_confirmed_similar_photo_count_with_subalbums()

            if not a.lat and not a.lon and a.geotagged_photo_count_with_subalbums:
                random_index = randint(0, a.geotagged_photo_count_with_subalbums - 1)
                random_photo = geotagged_photo_qs[random_index]
                a.lat = random_photo.lat
                a.lon = random_photo.lon
                a.geography = Point(x=float(a.lon), y=float(a.lat), srid=4326)
            else:
                random_index = randint(0, historic_photo_qs.count() - 1)
                random_photo = historic_photo_qs[random_index]
            a.cover_photo = random_photo
            if random_photo.flip:
                a.cover_photo_flipped = random_photo.flip

            a.light_save()
            time.sleep(0.2)
