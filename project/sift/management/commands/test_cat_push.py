# coding=utf-8
import ujson as json
from django.core.management.base import BaseCommand
import requests
from project.sift.models import CatPushDevice
from project.sift.settings import GOOGLE_API_KEY, GCM_ENDPOINT


# Command made for one use, review before running
class Command(BaseCommand):
    help = 'Test push notifications for Sift'

    def handle(self, *args, **options):
        headers = {
            'UserAgent': "GCM-Server",
            'Content-Type': 'application/json',
            'Authorization': 'key=' + GOOGLE_API_KEY
        }

        push_recipients = CatPushDevice.objects.all()
        values = {
            "registration_ids": [x.token for x in push_recipients],
            "data": {"album": 7, "title": "Elmar Einasto"},
            "collapse_key": "message"
        }
        values = json.dumps(values)

        response = requests.post(url=GCM_ENDPOINT, data=values, headers=headers)

        print response.content