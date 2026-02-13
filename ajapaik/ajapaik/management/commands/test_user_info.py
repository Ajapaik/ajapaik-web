import random
import re
import string
import time
from rest_framework.renderers import JSONRenderer

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from django.utils import timezone
from ajapaik.ajapaik.forms import AlbumSelectionForm, CuratorWholeSetAlbumsSelectionForm

from django.db.models import Sum, Q, Count, F
from ajapaik.utils import get_etag, calculate_thumbnail_size, convert_to_degrees, calculate_thumbnail_size_max_height, \
    distance_in_meters, angle_diff, last_modified, suggest_photo_edit
from ajapaik.ajapaik.utils import get_pagination_parameters

from ajapaik.ajapaik.serializers import CuratorAlbumSelectionAlbumSerializer, CuratorMyAlbumListAlbumSerializer, \
    CuratorAlbumInfoSerializer, FrontpageAlbumSerializer, DatingSerializer, \
    VideoSerializer, PhotoMapMarkerSerializer
import requests
from django.core.management import BaseCommand
from ajapaik.ajapaik.models import Photo, Album, _get_pseudo_slug_for_photo, GeoTag, AlbumPhoto, PhotoLike, ImageSimilarity, Licence, MyXtdComment, Dating, PhotoViewpointElevationSuggestion, PhotoSceneSuggestion, ImageSimilaritySuggestion, Transcription
from ajapaik.ajapaik.views import Photo, Album, Profile, _get_album_choices, _make_fullscreen
from django.conf import settings
from django.db.models import Q, Min, Max
from django.shortcuts import redirect, get_object_or_404, render
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation

from django.contrib.gis.db.models.functions import Distance, GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from ajapaik.ajapaik import forms
import json
import time
from datetime import timedelta
import numpy
from sorl.thumbnail import get_thumbnail

class Command(BaseCommand):
    help = 'Register user and run predefined requests against API'
    baseurl = 'http://localhost:8000'

    def get_mapdata(self):
       counter=0
       starttime=time.time()
       starttime2=time.time()

       limit_by_album=1
       qs = Photo.objects.filter( 
            lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True
       )
       album=Album.objects.get(id=100)

       album_photo_ids = album.get_historic_photos_queryset_with_subalbums().values_list('id', flat=True)
       qs2 = qs.filter(id__in=album_photo_ids)

       print(qs2.count())
       print(str(counter) + " c1: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       if album and limit_by_album:
            sa_ids = [album.id]
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                sa_ids.append(sa.id) 
            photos = qs.filter(albums__in = sa_ids).distinct()

       print(photos.count())
       print(str(counter) + " c1: " + str((time.time() - starttime2))) 
       starttime2 = time.time()



    def get_modalinfo(self):
       counter=0
       starttime=time.time()
       starttime2=time.time()

#       profile = request.get_user().profile  

       photo_qs = Photo.objects.filter(rephoto_of__isnull=True)
       photo_qs.count()

       print(str(counter) + " c1: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       photo_qs.filter(lat__isnull=False, lon__isnull=False).count()

       print(str(counter) + " c2: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

#       photo_similar_none_qs=photo_qs.exclude(Q(similar_photos=None) & Q(similar_photos=None))
#       print(photo_similar_none_qs.count())

#       print(str(counter) + " c3: " + str((time.time() - starttime2))) 
#       starttime2 = time.time()

#       photo_similar_none_qs=photo_qs.exclude(Q(similar_photos=None))
#       print(photo_similar_none_qs.count())

#       print(photo_similar_none_qs.only('id').query)
#       print(str(counter) + " c3: " + str((time.time() - starttime2))) 
#       starttime2 = time.time()

       rephoto_qs = Photo.objects.filter(rephoto_of__isnull=False)
       rephoto_qs.count()

       print(str(counter) + " c4: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       rephoto_qs.order_by('user').distinct('user').count()

       print(str(counter) + " c5: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       rephoto_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count()

       print(str(counter) + " c6: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

#       user_rephoto_qs = rephoto_qs.filter(user=profile)

       geotags_qs = GeoTag.objects
       geotags_qs.distinct('user').count()

       print(geotags_qs.distinct('user').only('user').query)

       print(str(counter) + " c7: " + str((time.time() - starttime2))) 
       starttime2 = time.time()
 
       person_annotation_qs = FaceRecognitionRectangle.objects.filter(deleted=None)
       person_annotation_qs.count(),

       print(str(counter) + " c8: " + str((time.time() - starttime2))) 
       starttime2 = time.time()


       person_annotation_with_person_album_qs = person_annotation_qs.exclude(subject_consensus=None)
       person_annotation_with_person_album_qs.count()

       print(str(counter) + " c9: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       person_annotation_with_subject_data_qs = person_annotation_qs.exclude(Q(gender=None) & Q(age=None))
       person_annotation_with_subject_data_qs.count()

       print(str(counter) + " c10: " + str((time.time() - starttime2))) 
       starttime2 = time.time()

       print(str(counter) + " c10: " + str((time.time() - starttime))) 


#       if cached_data is None:
#           cached_data = {
#            'photos_count': photo_qs.count(),
#            'contributing_users_count': geotags_qs.distinct('user').count(),
#            'photos_geotagged_count': photo_qs.filter(lat__isnull=False, lon__isnull=False).count(),
#            'rephotos_count': rephoto_qs.count(),
#            'rephotographing_users_count': rephoto_qs.order_by('user').distinct('user').count(),
#            'photos_with_rephotos_count': rephoto_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count(),
#            'photos_with_similar_photo_count': photo_qs.exclude(
#                Q(similar_photos=None) & Q(similar_photos=None)).count(),
#            'person_annotation_count': person_annotation_qs.count(),
#            'person_annotation_count_with_person_album': person_annotation_with_person_album_qs.count(),
#            'person_annotation_count_with_subject_data': person_annotation_with_subject_data_qs.count()
#        }

#   context = {
#        'user': request.get_user(),
#+        'total_photo_count': cached_data['photos_count'],
#+        'contributing_users': cached_data['contributing_users_count'],
#+        'total_photos_tagged': cached_data['photos_geotagged_count'],
#+        'rephoto_count': cached_data['rephotos_count'],
##        'photos_with_similar_photo_count': cached_data['photos_with_similar_photo_count'],
#+        'rephotographing_users': cached_data['rephotographing_users_count'],
#+        'rephotographed_photo_count': cached_data['photos_with_rephotos_count'],
#+        'person_annotation_count': cached_data['person_annotation_count'],
#+        'person_annotation_count_with_person_album': cached_data['person_annotation_count_with_person_album'],
#+        'person_annotation_count_with_subject_data': cached_data['person_annotation_count_with_subject_data'],
#-        'user_geotagged_photos': geotags_qs.filter(user=profile).distinct('photo').count(),
#-        'user_rephotos': user_rephoto_qs.count(),
#-        'user_rephotographed_photos': user_rephoto_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count()
#    }



    def get_photoslug(request=None, photo_id=None, pseudo_slug=None):
        starttime=time.time()
        starttime2=time.time()
        counter=0
        user_id=38
        profile = get_object_or_404(Profile, pk=user_id)
        is_current_user = False

        print(str(counter) + " c21: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

#?
        is_current_user = True
        if profile.user.is_anonymous:
            commented_pictures_qs_count = 0
        else:
            commented_pictures_qs_count = MyXtdComment.objects.filter(is_removed=False, user_id=profile.id).order_by(
                'object_pk').distinct('object_pk').count()

        print(commented_pictures_qs_count)
        print(str(counter) + " c21a: " + str((time.time() - starttime2))) 
        starttime2 = time.time()
##
        curated_pictures_qs_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=True).count()

#        print(curated_pictures_qs.only('id').order_by().query)

#        print(curated_pictures_qs.count())
        print(str(counter) + " c21b: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        datings_qs_count = Dating.objects.filter(profile_id=profile.id).distinct('photo').count()

#        print(datings_qs.count())
        print(str(counter) + " c21c: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        face_annotations_qs_count = FaceRecognitionRectangle.objects.filter(user_id=profile.id).order_by('photo_id').count()

#        print(face_annotations_qs.count())
        print(str(counter) + " c21d: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        face_annotations_pictures_qs_count = FaceRecognitionRectangle.objects.filter(user_id=profile.id).order_by('photo_id').distinct('photo').count()

#        print(face_annotations_pictures_qs.count())
        print(str(counter) + " c21e: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        geotags_qs_count = GeoTag.objects.filter(user_id=profile.id).exclude(type=GeoTag.CONFIRMATION).distinct('photo').count()

#        print(geotags_qs.count())
        print(str(counter) + " c21f: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        geotag_confirmations_qs_count = GeoTag.objects.filter(user_id=profile.id, type=GeoTag.CONFIRMATION).distinct('photo').count()

#        print(geotag_confirmations_qs.count())
        print(str(counter) + " c21g: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        object_annotations_qs_count = ObjectDetectionAnnotation.objects.filter(user_id=profile.id).order_by('photo_id').count()
#        print(object_annotations_qs.count())
        print(str(counter) + " c21h: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        object_annotations_pictures_qs_count = ObjectDetectionAnnotation.objects.filter(user_id=profile.id).order_by(
            'photo_id').distinct('photo').count()

 #       print(object_annotations_pictures_qs.count())
        print(str(counter) + " c21i: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        photolikes_qs_count = PhotoLike.objects.filter(profile_id=profile.id).distinct('photo').count()

#        print(photolikes_qs.count())
        print(str(counter) + " c21j: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        photo_viewpoint_elevation_suggestions_qs_ids = PhotoViewpointElevationSuggestion.objects.filter(
            proposer_id=profile.id).distinct('photo').values_list('photo_id', flat=True)

#        print(photo_viewpoint_elevation_suggestions_qs.count())
        print(str(counter) + " c21k: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        photo_scene_suggestions_qs_count = PhotoSceneSuggestion.objects.filter(proposer_id=profile.id).distinct('photo').exclude(
            photo_id__in=photo_viewpoint_elevation_suggestions_qs_ids).count()

        print("FOO")
        print(photo_scene_suggestions_qs_count)



#        print(photo_scene_suggestions_qs.count())
        print(str(counter) + " c21l1: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        photo_scene_suggestions_qs_count2 = PhotoSceneSuggestion.objects.filter(proposer_id=profile.id).exclude(photoviewpointelevationsuggestion__isnull=False).only('id')
        print(photo_scene_suggestions_qs_count2.query)

#PhotoSceneSuggestion.objects.filter(proposer_id=profile.id).distinct('photo').exclude(
#            photo_id__in=photo_viewpoint_elevation_suggestions_qs_ids).count()

#        print(photo_scene_suggestions_qs.count())
        print(str(counter) + " c21l2: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        rephoto_qs_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=False).count()

#        print(rephoto_qs.count())
        print(str(counter) + " c21m: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        rephotographed_pictures_qs_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=False).order_by(
            'rephoto_of_id').distinct('rephoto_of_id').count()

#        print(rephotographed_pictures_qs.count())
        print(str(counter) + " c21n: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        similar_pictures_qs_count = ImageSimilaritySuggestion.objects.filter(proposer=profile).distinct('image_similarity').count()

#        print(similar_pictures_qs.count())
        print(str(counter) + " c21s: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        transcriptions_qs_count = Transcription.objects.filter(user=profile).distinct('photo').count()

#        print(transcriptions_qs.count())
        print(str(counter) + " c21t: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        action_count = commented_pictures_qs_count + transcriptions_qs_count + \
                   object_annotations_qs_count + face_annotations_qs_count + \
                   curated_pictures_qs_count + geotags_qs_count + \
                   rephoto_qs_count + rephoto_qs_count + datings_qs_count + \
                   similar_pictures_qs_count + geotag_confirmations_qs_count + \
                   photolikes_qs_count + photo_scene_suggestions_qs_count + len(photo_viewpoint_elevation_suggestions_qs_ids)

        print(str(counter) + " c21y: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

#        user_points = 0
#        for point in profile.points.all():
#            user_points += point.points

#        print(user_points)

        print(str(counter) + " c21x: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        user_points=profile.points.aggregate(user_points=Sum('points'))['user_points']
        if user_points == None:
            user_points = 0

        print(user_points)

        print(str(counter) + " c21x: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        print(str(counter) + " total: " + str((time.time() - starttime))) 

#    return render(request, template, context)


    def handle(self, *args, **options):
#        self._get_filtered_data_for_frontpage2()
#        self.get_photoslug()
#        self.get_modalinfo()
        self.get_mapdata()


