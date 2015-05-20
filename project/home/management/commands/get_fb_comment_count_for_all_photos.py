from django.core.management.base import BaseCommand
import requests
from project.home.models import Photo
import ujson as json


class Command(BaseCommand):
    help = 'Ask how many comments each photo has on Facebook'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        photo_count = photos.count()
        start = 0
        while start <= photo_count:
            print str(start) + '...' + str(start + 500)
            query_string = 'http://graph.facebook.com/?ids='
            first = True
            for p in photos[start:start + 500]:
                if first:
                    query_string += 'http://ajapaik.ee/foto/' + str(p.id) + '/'
                    first = False
                else:
                    query_string += ',http://ajapaik.ee/foto/' + str(p.id) + '/'
            response = json.loads(requests.get(query_string).text)
            for k, v in response.iteritems():
                if 'comments' in v:
                    photo_id = k.split('/')[-2]
                    photo = Photo.objects.get(pk=photo_id)
                    photo.fb_comments_count = v['comments']
                    photo.save()
                    print "Updated " + photo_id
            start += 500