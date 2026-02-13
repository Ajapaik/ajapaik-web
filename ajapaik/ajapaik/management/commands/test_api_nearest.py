import random
import re
import string
import time

from django.template import Context, RequestContext
from ajapaik.ajapaik.serializers import AlbumSerializer, AlbumDetailsSerializer, PhotoSerializer
from ajapaik.ajapaik import forms

from django.contrib.gis.db.models.functions import Distance, GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
import requests
from django.core.management import BaseCommand
from ajapaik.ajapaik.models import Photo, Album, Profile, User

from django.db.models import Count, Q, Case, When, Value, BooleanField, IntegerField

from ajapaik.ajapaik import forms
import json
import time
from datetime import timedelta
from django.test.client import RequestFactory

class Command(BaseCommand):
    help = 'Register user and run predefined requests against API'
    baseurl = 'http://localhost:8000'

    def handle(self, *args, **options):
        self.factory = RequestFactory()
        request = self.factory.get('/customer/details')
        request.user=User.objects.get(pk=44387121)

        starttime = time.time()
        start=0
        end=1000
        longitude=24.942679
        latitude=60.1932118
        nearby_range=5000
        bbox=0.02

        print("* 1 : " + str((time.time() - starttime))) 

        user_profile=Profile.objects.get(pk=44387121)

        starttime = time.time()

        ref_location = Point(
            round(longitude, 5),
            round(latitude, 5),
            srid=4326
        )

        for bbox in [ 0.03, 0.04, 0.06, 0.1, 0.2, 0.4, 0.8, 1, 5]:
            photo_ids = Photo.objects.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, 
                lon__lte=longitude+bbox, lon__gte=longitude-bbox,
                lat__lte=latitude+bbox, lat__gte=latitude-bbox,
                ).values_list('id', flat=True)

            print(bbox)
            print

            if len(photo_ids)>nearby_range:
                break

        photos = Photo.objects.filter(id__in=photo_ids).annotate(
            distance=Distance(('geography'), ref_location)).filter(distance__lte=(D(m=nearby_range))).order_by(
            'distance')[start:end]

        print(photos.count())
        print("* 5 : " + str((time.time() - starttime))) 
        starttime = time.time()


        photos = PhotoSerializer.annotate_photos(
                    photos,
                    user_profile
                )
#        photos = photos \
#            .annotate(rephotos_count=Count('rephotos')) \
#            .annotate(likes_count=Count('likes'))\
#            .prefetch_related('source') \
#            .prefetch_related('rephotos') \
#            .annotate(uploads_count=Count(Case(When(rephotos__user=user_profile, then=1),
#                                               output_field=IntegerField()))) \
#            .annotate(favorited=Case(When(Q(likes__profile=user_profile) & Q(likes__profile__isnull=False),
#                                          then=Value(True)), default=Value(False), output_field=BooleanField()))


        p=PhotoSerializer(
                        instance=photos,
                        many=True,
                        context={'request': request}
                    ).data

        print("* 8 : " + str((time.time() - starttime))) 


#        ORIG
        starttime = time.time()
        start=0
        end=1000
        longitude=24.942679
        latitude=60.1932118
        nearby_range=5000
        bbox=0.02

        user_profile=Profile.objects.get(pk=44387121)
        photos = Photo.objects.filter(
                    lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, 
                    lon__lte=longitude+1, lon__gte=longitude-1,
                    lat__lte=latitude+1, lat__gte=latitude-1,
                    ).annotate(
                    distance=Distance(('geography'), ref_location)).filter(distance__lte=(D(m=nearby_range))).order_by(
                    'distance')[start:end]



        print(photos.values('id'))
        print("* 9a : " + str((time.time() - starttime))) 
        starttime = time.time()

        photos = PhotoSerializer.annotate_photos(
                    photos,
                    user_profile
                )

        print(photos.values('id').count())
        print("* 9a : " + str((time.time() - starttime))) 
        starttime = time.time()

        p=PhotoSerializer(
                        instance=photos,
                        many=True,
                        context={'request': request}
                    ).data


        print("* 9b : " + str((time.time() - starttime))) 

# NEW
        starttime = time.time()
        start=0
        end=100
        longitude=24.942679
        latitude=60.1932118
        nearby_range=5000
        bbox=0.02

        user_profile=Profile.objects.get(pk=44387121)

        photos = Photo.objects.filter(rephoto_of__isnull=True, ).annotate(distance=GeometryDistance("geography", ref_location)).order_by("distance")[start:end]
        photo_ids=photos.values_list('id', flat=True)
        photos=Photo.objects.filter(id__in=photo_ids).order_by(GeometryDistance("geography", ref_location));

#        photos_qs = Photo.objects.filter(rephoto_of__isnull=True).order_by(GeometryDistance("geography", ref_location)).values('id')

        print(photos.values('id').count())

        print("* 9c : " + str((time.time() - starttime))) 
        starttime = time.time()


        photos = PhotoSerializer.annotate_photos(
                    photos,
                    user_profile
                )
        print(photos.values('id').count())

        print("* 9d : " + str((time.time() - starttime))) 
        starttime = time.time()

        p=PhotoSerializer(
                        instance=photos,
                        many=True,
                        context={'request': request}
                    ).data


#        print(photos_qs.query)
#        print(photos.values('id').count())
        print("* 9e : " + str((time.time() - starttime))) 



#        qs = a.photos.filter(rephoto_of__isnull=True)
#        for sa in a.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
#            qs = qs | sa.photos.filter(rephoto_of__isnull=True)
#        photos=qs[start:end]

