import requests
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(latest_comment__isnull=False)
        query_string = 'https://graph.facebook.com/?id=%s&scrape=true'
        url_template = 'https://ajapaik.ee/foto/%d/'
        for p in photos:
            url = url_template % p.id
            requests.post(query_string % url)
