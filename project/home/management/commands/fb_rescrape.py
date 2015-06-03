from django.core.management.base import BaseCommand
import requests
from project.home.models import Photo


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(pk=8361)
        query_string = 'http://developers.facebook.com/tools/debug/og/object?q=%s'
        url_template = 'http://ajapaik.ee/foto/%d/'
        for p in photos:
            print p
            url = url_template % p.id
            requests.post(query_string % url)