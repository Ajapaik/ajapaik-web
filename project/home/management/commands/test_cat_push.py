import json
from django.core.management.base import BaseCommand
import requests
from project.settings import GOOGLE_API_KEY, GCM_ENDPOINT


class Command(BaseCommand):
    help = 'Test push notifications for Sift'

    def handle(self, *args, **options):
        headers = {
            'UserAgent': "GCM-Server",
            'Content-Type': 'application/json',
            'Authorization': 'key=' + GOOGLE_API_KEY
        }

        values = {
            #"registration_ids": [1],
            "data": {"msg": "Hakklihakeeks"},
            "collapse_key": "message"
        }
        values = json.dumps(values)

        response = requests.post(url=GCM_ENDPOINT, data=values, headers=headers)

        print response
        print response.content