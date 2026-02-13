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

class Command(BaseCommand):
    help = 'Test leaderboard'

    def _calculate_recent_activity_scores(self):
        starttime = time.time()

        c = min(5000, Points.objects.all().count())

        print("* 1.1 : " + str(time.time() - starttime)) 
        starttime = time.time()

        recent_actions = []
        if c > 0:
            five_thousand_actions_ago = Points.objects.order_by('-created')[c - 1].created
            recent_actions = Points.objects.filter(created__gt=five_thousand_actions_ago).values('user_id') \
                .annotate(total_points=Sum('points'))
        print("* 1.2 : " + str(time.time() - starttime)) 
        starttime = time.time()

        recent_action_dict = {}
        for each in recent_actions:
            recent_action_dict[each['user_id']] = each['total_points']
        print("* 1.3 : " + str(time.time() - starttime)) 
        starttime = time.time()

        recent_actors = Profile.objects.filter(pk__in=recent_action_dict.keys())
        print("* 1.4 : " + str(time.time() - starttime)) 
        starttime = time.time()

        for user_id in recent_action_dict:
#            p=Profile.objects.filter(pk=user_id).first()
#            p=Profile.objects.filter(pk=user_id,score_recent_activity__ne=recent_action_dict[user_id]).first()
            print(user_id)
#            print(p.score)
#            if p:
#                p.score_recent_activity = 0
            
 #           each.score_recent_activity = recent_action_dict[each.pk]
 #           each.save()
        print("* 1.5 : " + str(time.time() - starttime)) 
        starttime = time.time()
        if 1:
           exit(1)

    # Profile.objects.bulk_update(recent_actors, update_fields=['score_recent_activity'])
    # Check for people who somehow no longer have actions among the last 5000
        orphan_profiles = Profile.objects.filter(score_recent_activity__gt=0).exclude(pk__in=[x.pk for x in recent_actors])
        print("* 1.6 : " + str(time.time() - starttime)) 
        starttime = time.time()

        orphan_profiles.update(score_recent_activity=0)

        print("* 1.7 : " + str(time.time() - starttime)) 
        starttime = time.time()



    def handle(self, *args, **options):

#        starttime2 = time.time()
        starttime = time.time()


        print(Profile.objects.all().count())
        print("* 1 : " + str(time.time() - starttime)) 
        starttime = time.time()



        album_leaderboard = None
        general_leaderboard = None
        print("* 1 : " + str(time.time() - starttime)) 
        starttime = time.time()

        profile = Profile.objects.first()
        print("* 2 : " + str(time.time() - starttime)) 
        starttime = time.time()
        print(profile)


        self._calculate_recent_activity_scores()
        print("* 3 : " + str(time.time() - starttime)) 
        starttime = time.time()

        profile_rank = Profile.objects.filter(score_recent_activity__gt=profile.score_recent_activity,
                                              first_name__isnull=False, last_name__isnull=False).count() + 1
        print("* 4 : " + str(time.time() - starttime)) 
        starttime = time.time()

        leaderboard_queryset = Profile.objects.filter(
            Q(first_name__isnull=False, last_name__isnull=False, score_recent_activity__gt=0) |
            Q(pk=profile.id)).order_by('-score_recent_activity')
        print("* 5 : " + str(time.time() - starttime)) 
        starttime = time.time()

        start = profile_rank - 2
        if start < 0:
            start = 0
        nearby_users = leaderboard_queryset[start:profile_rank + 1]
        print("* 6 : " + str(time.time() - starttime)) 
        starttime = time.time()

        n = start + 1
        for each in nearby_users:
            if each.user_id == profile.id:
                each.is_current_user = True
            each.position = n
            n += 1
        print("* 7 : " + str(time.time() - starttime)) 
        starttime = time.time()

        general_leaderboard = nearby_users
        print(general_leaderboard)

        print("* 8 : " + str(time.time() - starttime)) 

#        a=Album.objects.get(pk=52090)
#        print(a)
#        a.created='2021-10-28 09:25:10.380798+00:00'
#        a.save()
#        print(a.created)

#        if 1:
#            exit(1)
#        starttime2 = time.time()
#        starttime = time.time()
#        albums = _get_album_choices(None,0,1)
#        print("* 1 : " + str(time.time() - starttime)) 
