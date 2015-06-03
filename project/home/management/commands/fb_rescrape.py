from django.core.management.base import BaseCommand
import requests
from project.home.models import Photo


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = Photo.objects.order_by('latest_comment')
        query_string = 'http://graph.facebook.com/?id=%s&scrape=true'
        url_template = 'http://ajapaik.ee/foto/%d/'
        for p in photos:
            print p.id
            url = url_template % p.id
            requests.post(query_string % url)