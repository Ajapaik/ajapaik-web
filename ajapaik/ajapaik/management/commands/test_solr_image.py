from random import randint
from django.contrib.gis.geos import Point
import time

import os
import re

from ajapaik.ajapaik.serializers import AlbumSerializer
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Sum, Q
from ajapaik.ajapaik.models import Photo, Album, Points, ImageSimilarity, Profile, GeoTag, Profile
from django.db import connection
from ajapaik.ajapaik.views import _get_album_choices, calculate_thumbnail_size

from sorl.thumbnail import get_thumbnail
from django.conf import settings
from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Test leaderboard'

    def handle(self, *args, **options):
        thumb_size=400
        p = Photo.objects.get(pk=68415)

        print("Full resolution")
        print(f'{settings.MEDIA_ROOT}/{p.image}')

        thumb_str = f'{str(thumb_size)}x{str(thumb_size)}'
        im = get_thumbnail(p.image, thumb_str, upscale=False)

        print("Thumbnail")
        print(f'{settings.MEDIA_ROOT}/{im.name}')


       

