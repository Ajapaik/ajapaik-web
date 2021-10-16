from random import randint
from django.contrib.gis.geos import Point
import time

import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Sum
from ajapaik.ajapaik.models import Photo, Album, Points, ImageSimilarity
from django.db import connection


class Command(BaseCommand):
    help = 'Update photo directory from ./media/uploads to ./media/uploads/YYYY/MM'

    def handle(self, *args, **options):

       # Actual update loop
       #for a_id in album_ids:
       albums = Album.objects.exclude(atype__in=[Album.AUTO, Album.FAVORITES])
       for a in albums:
            ret={}
            starttime = time.time()

            # Populate parent+subalbums list
            sa_ids=[a.id]
            for sa in a.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
               sa_ids.append(sa.id)

            # Get photos
            qs = Photo.objects.filter(rephoto_of__isnull=True).prefetch_related('albumphoto').filter(albumphoto__album__in=sa_ids)
            historic_photo_qs=qs.distinct('id').values('id').order_by()
            historic_photos_list=list(historic_photo_qs.values_list('id', flat=True))

            # Number of historical photos
            ret['historic_photo_count']=len(historic_photos_list)

            # Move to next album if there is no photos
            if ret['historic_photo_count']==0:
                continue

            # Number of geotagged photos
            geotagged_photo_qs=historic_photo_qs.filter(lat__isnull=False, lon__isnull=False).order_by()
            ret['geotagged_photo_count']=geotagged_photo_qs.count()

            # Number of rephotos
            qs = Photo.objects.filter(rephoto_of__in=historic_photos_list).order_by()
            rephoto_qs=qs.distinct('id').values('id').order_by()

            # Add rephotos to all_photos_list to keep backwards compability with older stats
            all_photos_list=historic_photos_list
            for p in rephoto_qs:
                all_photos_list.append(p['id'])

            # This needs to be after for loop as it will pre-load data for the rephoto_qs.count() as byproduct.
            ret['rephoto_count']=rephoto_qs.count()

            # Comment count
            ret['comment_count']=Photo.objects.filter(id__in=all_photos_list, comment_count__gt=0).order_by().aggregate(Sum('comment_count'))['comment_count__sum']
            if ret['comment_count']==None:
                ret['comment_count']=0

            # Similar photos count
            imagesimilarity_qs=ImageSimilarity.objects.filter(from_photo__in=all_photos_list).only('pk').distinct('pk').order_by()
            ret['similar_photo_count']=imagesimilarity_qs.count()

            # Confirmed similar photos count 
            ret['confirmed_similar_photo_count']=imagesimilarity_qs.filter(confirmed=True).count()

            a.photo_count_with_subalbums = ret['historic_photo_count']
            a.geotagged_photo_count_with_subalbums = ret['geotagged_photo_count']
            a.comments_count_with_subalbums = ret['comment_count']
            a.similar_photo_count_with_subalbums = ret['similar_photo_count']
            a.confirmed_similar_photo_count_with_subalbums = ret['confirmed_similar_photo_count']

            print(str(a) + "("+ str(a.id) + ")\t"+  str(ret['historic_photo_count']) + "\t" + str(time.time() - starttime)) 

            if not a.lat and not a.lon and a.geotagged_photo_count_with_subalbums:
                random_index = randint(0,  ret['historic_photo_count'] - 1)
                random_photo = Photo.objects.get(pk=historic_photos_list[random_index])
                a.lat = random_photo.lat
                a.lon = random_photo.lon
                a.geography = Point(x=float(a.lon), y=float(a.lat), srid=4326)
            else:
                random_index = randint(0,  ret['historic_photo_count'] - 1)
                random_photo = Photo.objects.get(pk=historic_photos_list[random_index])

            a.cover_photo = random_photo
            if random_photo.flip:
                a.cover_photo_flipped = random_photo.flip

            a.light_save()







