import random
import re
import string
import time
import operator
from django.db import connection

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
from ajapaik.ajapaik.models import Photo, Album, _get_pseudo_slug_for_photo, GeoTag, AlbumPhoto, PhotoLike, ImageSimilarity, Licence
from ajapaik.ajapaik.views import Photo, Album, Profile, _get_album_choices, _make_fullscreen
from django.conf import settings
from django.db.models import Q, Min, Max
from django.shortcuts import redirect, get_object_or_404, render

from django.contrib.gis.db.models.functions import Distance, GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from ajapaik.ajapaik import forms
import json
import time
from datetime import timedelta
import numpy
from sorl.thumbnail import get_thumbnail
from ajapaik.ajapaik.stats_sql import AlbumStats

class Command(BaseCommand):

#    def get_user_geotagged_photo_count_sql(self, albums, user_id):
#        albums_str=",".join(map(str, map(int,albums)))
#        ret=0
#
#        if user_id and albums_str and user_id>0:
#            user_id_str=str(int(user_id))
#            sql="SELECT count(distinct(g.photo_id)) as user_geotagged_photo_count"
#            sql=sql + " FROM project_albumphoto as ap, project_geotag as g" 
#            sql=sql + " WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id AND g.user_id=" + user_id_str

#            cursor = connection.cursor()
#            cursor.execute(sql)
#            row = cursor.fetchone()
#            ret = row[0] or 0

#        return ret

#    def get_geotagging_user_count_sql(self, albums):
#        albums_str=",".join(map(str, map(int,albums)))
#        ret=0
#        if albums:
#            sql="SELECT count(distinct(g.user_id)) as geotagging_user_count ";
#            sql=sql + " FROM project_albumphoto as ap, project_geotag as g ";
#            sql=sql + " WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id"
#            cursor = connection.cursor()
#            cursor.execute(sql)
#            row = cursor.fetchone()
#            ret = row[0] or 0
#        return ret

#    def get_rephoto_stats_sql(self, albums, user_id):
#        albums_str=",".join(map(str, map(int,albums)))
#
#        ret={}
#        ret['user_rephotographed_photo_count']=0
#        ret['user_rephoto_count']=0
#        ret['rephoto_user_count']=0
#        ret['rephotographed_photo_count']=0
#        ret['rephoto_count']=0
#        ret['user_made_all_rephotos']=False
#        if albums_str and user_id and user_id>0:
#            user_id_str=str(int(user_id))
#            sql="SELECT COUNT(DISTINCT((p2.user_id=" + user_id_str + ")::int*p2.rephoto_of_id)) AS user_rephotographed_photo_count, "
#            sql=sql + " COUNT(DISTINCT((p2.user_id=" + user_id_str + ")::int*p2.id)) AS user_rephoto_count, "
#            sql=sql + " COUNT(DISTINCT(p2.user_id)) AS rephoto_user_count, "
#            sql=sql + " COUNT(DISTINCT(p1.id))  AS rephotographed_photo_count, "
#            sql=sql + " COUNT(DISTINCT(p2.id))  AS rephoto_count "
#            sql=sql + " FROM project_albumphoto AS ap, project_photo AS p1, project_photo AS p2 "
#            sql=sql + " WHERE "
#            sql=sql + " ap.album_id IN (" + albums_str + ") "
#            sql=sql + " AND p1.id=ap.photo_id ";
#            sql=sql + " AND p2.rephoto_of_id=p1.id"
#            cursor = connection.cursor()
#            cursor.execute(sql)
#            row = cursor.fetchone()
#            columns = [col[0] for col in cursor.description]
#            ret=dict(zip(columns, row))
#            ret['user_made_all_rephotos'] = (ret['rephoto_user_count'] == 1) and (ret['user_rephoto_count'] == ret['rephoto_count'])
#            print(ret)
#        return ret

#    def get_album_curators_sql(self, albums): 
#        albums_str=",".join(map(str, map(int,albums)))

#        album_types=[AlbumPhoto.UPLOADED, AlbumPhoto.CURATED, AlbumPhoto.RECURATED]
#        album_types_str=",".join(map(str, album_types))
#        ret=[]
#        if albums_str:
#            sql="SELECT pp.user_id ";
#            sql= sql + " FROM project_profile as pp, project_albumphoto as ap ";
#            sql= sql + " WHERE ap.type IN (" + album_types_str +") ";
#            sql= sql + " AND ap.album_id IN ("+ albums_str +") ";
#            sql= sql + " AND ap.profile_id=pp.user_id ";
#            sql= sql + " GROUP BY pp.user_id ";
#            sql= sql + " ORDER BY sum(1) DESC"

#            profiles=Profile.objects.raw(sql)
#            for profile in profiles:
#                ret.append(profile)

#        return ret


    def get_historic_photos_subalbums(t, self):
        sa_ids = [self.id]
        for sa in self.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            sa_ids.append(sa.id)
        return sa_ids


    def t_get_historic_photos_queryset_with_subalbums(t, self):
        sa_ids = [self.id]
        for sa in self.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            sa_ids.append(sa.id)

        qs = Photo.objects.filter(rephoto_of__isnull=True).select_related('albumphoto').filter(albumphoto__album__in=sa_ids)
        return qs.distinct('id')

    def t_get_all_photos_queryset_with_subalbums(self, album):
        historic_photo_qs=self.get_historic_photos_queryset_with_subalbums().order_by()
        rephoto_qs=Photo.objects.filter(rephoto_of__isnull=False, rephoto_of__in=historic_photo_qs.values('id').order_by()).values('id').distinct('id').order_by()

        historic_photo_list = list(historic_photo_qs.values_list('id', flat=True))
        for p in rephoto_qs:
            historic_photo_list.append(p['id'])

        qs=Photo.objects.filter(id__in=historic_photo_list)
        return qs.distinct('pk')

    def get_album_modal_info2(self, profile, album):
        starttime=time.time()

#        profile = Profile.objects.get(pk=38)
#        album = Album.objects.get(pk=21)

        subalbums = [album.id]
        for sa in album.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            subalbums.append(sa.id)

        rephotostats=AlbumStats.get_rephoto_stats_sql(subalbums, profile.pk)

        context={}
        context['user_geotagged_photo_count']     = AlbumStats.get_user_geotagged_photo_count_sql(subalbums, profile.pk)
        context['geotagging_user_count']          = AlbumStats.get_geotagging_user_count_sql(subalbums)
        context['rephoto_count']                  = rephotostats["rephoto_count"]
        context['rephoto_user_count']             = rephotostats["rephoto_user_count"] 
        context['rephotographed_photo_count']     = rephotostats["rephotographed_photo_count"] 
        context['user_rephoto_count']             = rephotostats["user_rephoto_count"]
        context['user_rephotographed_photo_count']= rephotostats["user_rephotographed_photo_count"]
        context['user_made_all_rephotos']         = rephotostats['user_made_all_rephotos']
        context['similar_photo_count']            = album.similar_photo_count_with_subalbums 
        context['confirmed_similar_photo_count']  = album.confirmed_similar_photo_count_with_subalbums
        context['album_curators']                 = AlbumStats.get_album_curators_sql([album.id])

        print(context)
        print("A1" + ": " + str(time.time() - starttime))
        return context



    def get_album_modal_info(self, profile, album):
        starttime=time.time()
        context={}
        if True:
#        form = AlbumInfoModalForm(request.GET)

#    if form.is_valid():
#        album = form.cleaned_data['album']
#        context = {'album': album, 'link_to_map': form.cleaned_data['linkToMap'],
#                   'link_to_game': form.cleaned_data['linkToGame'],
#                   'link_to_gallery': form.cleaned_data['linkToGallery'],
#                   'fb_share_game': form.cleaned_data['fbShareGame'], 'fb_share_map': form.cleaned_data['fbShareMap'],
#                   'fb_share_gallery': form.cleaned_data['fbShareGallery'],
#                   'total_photo_count': album.photo_count_with_subalbums,
#                   'geotagged_photo_count': album.geotagged_photo_count_with_subalbums}

##            starttime=time.time()

##            albums=self.get_historic_photos_subalbums(album)
##            albums_str=",".join(map(str, albums))
##            cursor = connection.cursor()
##            objs=cursor.execute("SELECT count(distinct(g.photo_id)) as c FROM project_albumphoto as ap, project_geotag as g WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id AND g.user_id=38")
##            row = cursor.fetchone()
##            print(row)
##            print("A2" + ": " + str(time.time() - starttime))
##            starttime=time.time()


##            t=self.t_get_historic_photos_queryset_with_subalbums(album).select_related('photo').select_related('geotags').filter(geotags__user=profile).values('geotags__id').count()
##            print(t)
##            print("A1" + ": " + str(time.time() - starttime))
##            starttime=time.time()

##            t=album.get_historic_photos_queryset_with_subalbums().prefetch_related('photo').prefetch_related('geotags').filter(geotags__user=profile).values('geotags__photo_id').order_by('geotags__photo_id').distinct('geotags__photo_id').count()
##            print(t)
##            print("A0" + ": " + str(time.time() - starttime))
##            starttime=time.time()

##            t=self.t_get_historic_photos_queryset_with_subalbums(album).select_related('photo').select_related('geotags').filter(geotags__user=profile).values('geotags__photo_id').order_by('geotags__photo_id').distinct('geotags__photo_id').count()
##            print(t)
##            print("A1" + ": " + str(time.time() - starttime))
##            starttime=time.time()


            album_photo_ids = album.get_all_photos_queryset_with_subalbums().values_list('id', flat=True)
            geotags_for_album_photos = GeoTag.objects.filter(photo_id__in=album_photo_ids)

##            print("A" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['user_geotagged_photo_count'] = geotags_for_album_photos.filter(user=profile).distinct('photo_id').count()
#            print(context['user_geotagged_photo_count'])

##            print("B" + ": " + str(time.time() - starttime))
##            starttime=time.time()

##            objs=cursor.execute("SELECT count(distinct(g.user_id)) as c FROM project_albumphoto as ap, project_geotag as g WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id")
##            row = cursor.fetchone()
##            print(row)
##            print("C1" + ": " + str(time.time() - starttime))
##            starttime=time.time()



#            t=album.get_historic_photos_queryset_with_subalbums().prefetch_related('photo').prefetch_related('geotags').values('geotags__user').order_by('geotags__user').distinct('geotags__user').count()
#            t=album.get_historic_photos_queryset_with_subalbums().select_related('photo').select_related('geotags').values('geotags__user').order_by('geotags__user').distinct('geotags__user').count()
#            t=album.get_historic_photos_queryset_with_subalbums().prefetch_related('photo').prefetch_related('geotags').values('geotags__user').count()
#            print(t)

##            print("C0" + ": " + str(time.time() - starttime))
##            starttime=time.time()


#            print(str(geotags_for_album_photos.distinct('user').only(user).query))
            context['geotagging_user_count'] = geotags_for_album_photos.distinct('user').count()
#            print(context['geotagging_user_count'])


##            print("C_old" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['rephoto_count'] = album.rephoto_count_with_subalbums
##            print("D" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            rephotos_qs = album.get_rephotos_queryset_with_subalbums()
##            print("E" + ": " + str(time.time() - starttime))
##            starttime=time.time()

##            objs=cursor.execute("SELECT count(distinct((p2.user_id=38)::int*p2.rephoto_of_id)) as u_photos, count(distinct(p2.id*(p2.user_id=38)::int)) as uc, count(distinct(p2.user_id)) as u, count(distinct(p2.id)) as c FROM project_albumphoto as ap, project_photo as p1, project_photo as p2 WHERE ap.album_id IN (" + albums_str + ") AND p1.id=ap.photo_id AND p2.rephoto_of_id=p1.id")
##            row = cursor.fetchone()
##            print(row)
##            print("F0" + ": " + str(time.time() - starttime))
##            starttime=time.time()


            print(str(rephotos_qs.order_by('user_id').distinct('user_id').only('user_id').query))
            context['rephoto_user_count'] = rephotos_qs.order_by('user_id').distinct('user_id').count()
##            print(context['rephoto_user_count'])
##            print("F" + ": " + str(time.time() - starttime))
##            starttime=time.time()

##            objs=cursor.execute("SELECT count(distinct(p.id)) as c FROM project_albumphoto as ap, project_photo as p WHERE ap.album_id IN (" + albums_str + ") AND p.id=ap.photo_id AND p.rephoto_count>0")
##            row = cursor.fetchone()
##            print(row)
##            print("G0" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['rephotographed_photo_count'] = rephotos_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count()
##           print(album.rephoto_count_with_subalbums)
##           print(context['rephotographed_photo_count'])

##            print("G" + ": " + str(time.time() - starttime))
##            starttime=time.time()

#            t=Album.objects(pk__in=album.get_historic_photos_queryset_with_subalbums().values_only('id')).count()
#            print(t)

##            print("G1" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            album_user_rephotos = rephotos_qs.filter(user=profile)
            context['user_rephoto_count'] = album_user_rephotos.count()
##            print(context['user_rephoto_count'])
##            print("H" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['user_rephotographed_photo_count'] = album_user_rephotos.order_by('rephoto_of_id').distinct('rephoto_of_id').count()
##            print(context['user_rephotographed_photo_count'])
##            print("I" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            if context['rephoto_user_count'] == 1 and context['user_rephoto_count'] == context['rephoto_count']:
                context['user_made_all_rephotos'] = True
            else:
                context['user_made_all_rephotos'] = False

            context['similar_photo_count'] = album.similar_photo_count_with_subalbums
##            print("J" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['confirmed_similar_photo_count'] = album.confirmed_similar_photo_count_with_subalbums
##            print("K" + ": " + str(time.time() - starttime))
##            starttime=time.time()


#            t=Profile.objects.filter(points__gt=5).prefetch_related('album_photo_links').filter(album_photo_links__album=album,
#                                                                     album_photo_links__type__in=[AlbumPhoto.UPLOADED, AlbumPhoto.CURATED,AlbumPhoto.RECURATED]).annotate(count=Count('user_id')).order_by('-count')[:10]


##            album_types=[AlbumPhoto.UPLOADED, AlbumPhoto.CURATED, AlbumPhoto.RECURATED]
##            album_types_str=",".join(map(str, album_types))

##            t=Profile.objects.raw("SELECT pp.user_id FROM project_profile as pp, project_albumphoto as ap WHERE ap.type IN (" + album_types_str +") AND ap.album_id IN ("+ str(album.id) +") and ap.profile_id=pp.user_id GROUP BY pp.user_id ORDER BY sum(1) DESC")
##            profiles=[]
##            for u in t:
##                profiles.append(u)

##            print(profiles)
##            print("L0" + ": " + str(time.time() - starttime))
##            starttime=time.time()


#            # Get all users that have either curated into selected photo set or re-curated into selected album
            users_curated_to_album = AlbumPhoto.objects.filter(
                                                           photo_id__in=album_photo_ids, 
                                                            profile__isnull=False, 
                                                            album=album,
                                                            type__in=[AlbumPhoto.UPLOADED, AlbumPhoto.CURATED, 
                                                            AlbumPhoto.RECURATED]
                                                        ).values('profile').annotate(count=Count('profile'))
##            print("L" + ": " + str(time.time() - starttime))
##            starttime=time.time()


            user_score_dict = {}
            for u in users_curated_to_album:
                user_score_dict[u['profile']] = u['count']

##            print("L1" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            album_curators = Profile.objects.filter(user_id__in=user_score_dict.keys(), first_name__isnull=False,
                                                last_name__isnull=False)

##            print("L2" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            user_score_dict = [x[0] for x in sorted(user_score_dict.items(), key=operator.itemgetter(1), reverse=True)]
##            print(album_curators)

##            print("L3" + ": " + str(time.time() - starttime))
##            starttime=time.time()


##            print("M" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            album_curators = list(album_curators)
            album_curators.sort(key=lambda z: user_score_dict.index(z.id))
##            print(album_curators)

##            print("N" + ": " + str(time.time() - starttime))
##            starttime=time.time()

            context['album_curators'] = album_curators
            print("O" + ": " + str(time.time() - starttime))
            starttime=time.time()

            if album.lat and album.lon:
                ref_location = Point(x=album.lon, y=album.lat, srid=4326)
#                context['nearby_albums'] = Album.objects.filter(lat__isnull=False, lon__isnull=False, id__ne=album.id ).annotate(
#                                          distance=GeometryDistance(('geography'), ref_location)).order_by('distance')[:3]

#                photos = photos.annotate(distance=GeometryDistance(('geography'), ref_location)).order_by('-distance')


                context['nearby_albums'] = Album.objects \
                                           .filter(
                    geography__dwithin=(ref_location, D(m=5000)),
                    is_public=True,
                    atype=Album.CURATED,
                    id__ne=album.id
                ).order_by('?')[:3]
#                )[:3]
#            album_id_str = str(album.id)
            print(context)
            print("O2" + ": " + str(time.time() - starttime))

        return context



    def handle(self, *args, **options):
# Kimmo + Helsinki
        profile = Profile.objects.get(pk=44387121)
#        album = Album.objects.get(pk=76397)
        album = Album.objects.get(pk=22)
#        album = Album.objects.get(pk=1)

# Vahur + Tallinna
#        profile = Profile.objects.get(pk=38)
#        album = Album.objects.get(pk=21)


        t1=self.get_album_modal_info2(profile, album)
        t2=self.get_album_modal_info(profile, album)

        for key in t1:
            print(str(t1[key]) + "\n" + str(t2[key]) + "\n" )
#        print(json.dumps(t))


