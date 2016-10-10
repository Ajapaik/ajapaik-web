import requests
from django.core.management.base import BaseCommand

from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(latest_comment__isnull=False)
        query_string = 'https://graph.facebook.com/?id=%s&scrape=true'
        url_template = 'http://fotodugnad.ra.no/photo/%d/'
        for p in photos:
            print p.id
            url = url_template % p.id
            requests.post(query_string % url)
