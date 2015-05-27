from django.core.management.base import BaseCommand
import requests
from project.home.facebook import APP_ID
from project.home.models import Photo
from project.settings import FACEBOOK_APP_SECRET
import ujson as json


class Command(BaseCommand):
    help = 'Get all Facebook comments for our photos, mark earliest, latest and comment count'

    def handle(self, *args, **options):
        or_clause = ''
        photos = Photo.objects.order_by('created')[:500]
        first = True
        for p in photos:
            if first:
                or_clause += "'http://ajapaik.ee/foto/" + str(p.id) + "/'"
                first = False
            else:
                or_clause += " OR url = 'http://ajapaik.ee/foto/" + str(p.id) + "/'"
        fql_string = "SELECT text, id, parent_id, post_fbid, fromid, time FROM comment WHERE object_id IN (SELECT comments_fbid FROM link_stat WHERE url = %s) ORDER BY time DESC limit 500" % or_clause
        response = json.loads(requests.get('https://graph.facebook.com/fql?access_token=%s&q=%s' % (APP_ID + '|' + FACEBOOK_APP_SECRET, fql_string)).text)