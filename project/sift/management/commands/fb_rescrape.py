from django.core.management.base import BaseCommand
import requests
from project.sift.models import CatPhoto


class Command(BaseCommand):
    help = 'Rescrape all our photo URLs'

    def handle(self, *args, **options):
        photos = CatPhoto.objects.all()
        query_string = 'http://graph.facebook.com/?id=%s&scrape=true'
        url_template = 'http://sift.pics/photo/%d/'
        for p in photos:
            print p.id
            url = url_template % p.id
            requests.post(query_string % url)
s