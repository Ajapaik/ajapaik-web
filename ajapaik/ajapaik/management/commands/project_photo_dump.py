# coding=utf-8
import json as json
from django.core.management.base import BaseCommand
import requests
import json
import copy
from django.core import serializers
from ajapaik.ajapaik.models import Photo


# Command made for one use, review before running
class Command(BaseCommand):
    help = 'Test push notifications for Sift'

    def handle(self, *args, **options):
        photos = json.loads(serializers.serialize("json", Photo.objects.filter(rephoto_of__isnull=True).all()))
        print(json.dumps(photos, indent=4, sort_keys=True))

