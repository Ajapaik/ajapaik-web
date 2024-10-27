import requests
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(latest_comment__isnull=False)

        for p in photos:
            url = f'https://ajapaik.ee/photo/{p.id}'
            requests.post(f'https://graph.facebook.com/?id={url}&scrape=true')
