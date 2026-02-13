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


        album=52090
        album=65516
        album=65720 # Paasitornin kävelykierros
        album=65808 #  Inha
        album=68143 #  Kansallismuseon kierros 68143
        album=76392 #  Valokuvakierros Tamminiemessä
#        album=51223
#        album=50339
#        album=22
#        album=21
#        album=1

        a=Album.objects.get(pk=album)
        print(a)
        print(a.created)
        a.created='2022-11-12 11:05:10.380798+00:00'
        print(a.created)
        a.save()
