import random
import re
import string
import time
from django.conf import settings

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
        print("grep -P \"" + '|'.join(settings.BOT_USER_AGENTS) + "\"\n")

