import datetime
from django.core.management.base import BaseCommand
import requests
from project.ajapaik.facebook import APP_ID
from project.ajapaik.models import Photo, PhotoComment
from project.ajapaik.settings import FACEBOOK_APP_SECRET
import ujson as json


class Command(BaseCommand):
    help = 'Get all Facebook comments for our photos, mark earliest, latest and comment count'

    def handle(self, *args, **options):
        # First get the real FB ids for photos that don't have them in batches of 250
        photos = Photo.objects.filter(fb_object_id__isnull=True)
        photo_count = photos.count()
        start = 0
        end = 250
        while start <= photo_count:
            or_clause = ''
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if first:
                    or_clause += "'http://ajapaik.ee/foto/" + str(p.id) + "/'"
                    first = False
                else:
                    or_clause += " OR url = 'http://ajapaik.ee/foto/" + str(p.id) + "/'"
            if len(or_clause) > 0:
                fql_string = "SELECT comments_fbid, url FROM link_stat WHERE url = %s limit 250" % or_clause
                response = json.loads(requests.get('https://graph.facebook.com/fql?access_token=%s&q=%s' % (APP_ID + '|' + FACEBOOK_APP_SECRET, fql_string)).text)
                if 'data' not in response:
                    print fql_string
                    print response
                    return
                for each in response['data']:
                    photo_id = each['url'].split('/')[-2]
                    photo = photos.get(pk=photo_id)
                    photo.fb_object_id = each['comments_fbid']
                    photo.light_save()
            start += 250
            end += 250
        # Now use the ids to request all comments from Facebook
        photos = Photo.objects.filter(fb_object_id__isnull=False).prefetch_related('comments')
        photo_count = photos.count()
        start = 0
        end = 250
        # Empty comments table
        for pc in PhotoComment.objects.all():
            pc.delete()
        while start <= photo_count:
            ids = ''
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if len(p.fb_object_id) > 0:
                    if first:
                        ids += str(p.fb_object_id)
                        first = False
                    else:
                        ids += ',' + str(p.fb_object_id)
            if len(ids) > 0:
                fql_string = "SELECT text, id, parent_id, object_id, fromid, time FROM comment WHERE object_id IN (%s)" % ids
                response = json.loads(requests.get('https://graph.facebook.com/fql?access_token=%s&q=%s' % (APP_ID + '|' + FACEBOOK_APP_SECRET, fql_string)).text)
                if 'data' not in response:
                    print fql_string
                    print response
                    return
                for each in response['data']:
                    existing_comment = PhotoComment.objects.filter(fb_comment_id=each['id']).first()
                    if existing_comment:
                        existing_comment.text = each['text']
                        existing_comment.save()
                    else:
                        new_photo_comment = PhotoComment(
                            fb_comment_id=each['id'],
                            fb_comment_parent_id=each['parent_id'],
                            fb_user_id=each['fromid'],
                            fb_object_id=each['object_id'],
                            text=each['text'],
                            created=datetime.datetime.fromtimestamp(each['time']),
                            photo=photos.get(fb_object_id=each['object_id'])
                        )
                        new_photo_comment.save()
            start += 250
            end += 250