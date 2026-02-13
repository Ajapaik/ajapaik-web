import random
import re
import string
import time

import requests
from django.core.management import BaseCommand
from ajapaik.ajapaik.models import Photo, Album

from django.db.models import Q

from ajapaik.ajapaik import forms
import json
import time
from datetime import timedelta

class Command(BaseCommand):
    help = 'Register user and run predefined requests against API'
    baseurl = 'http://localhost:8000'

    def handle(self, *args, **options):

        starttime = time.time()
        start=0
        end=100000
#        album=50767
        album=7


        album=24675
#        album=51223
#        album=50339
#        album=22
#        album=21
#        album=1

        photos = Photo.objects.filter(
                Q(albums=album)
                | (Q(albums__subalbum_of=album)
                   & ~Q(albums__atype=Album.AUTO)),
                rephoto_of__isnull=True
            )[start:end]

        print(len(photos))
        print("* 6 : " + str((time.time() - starttime))) 


        starttime = time.time()
        a=Album.objects.get(pk=album)
        qs = a.photos.filter(rephoto_of__isnull=True)
        for sa in a.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            qs = qs | sa.photos.filter(rephoto_of__isnull=True)
        photos=qs[start:end]

        print(len(photos))
        print("* 7 : " + str((time.time() - starttime))) 
