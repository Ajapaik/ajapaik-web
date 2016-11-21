import ujson as json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from project.ajapaik.facebook import APP_ID
from project.ajapaik.models import Photo, PhotoComment


class Command(BaseCommand):
    help = 'Get all Facebook comments for our photos'

    def handle(self, *args, **options):
        # First get the real FB ids for photos that don't have them in batches of 250
        photos = Photo.objects.filter(fb_object_id__isnull=True)
        photo_count = photos.count()
        start = 0
        end = 250
        while start <= photo_count:
            or_clause = 'ids='
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if first:
                    or_clause += "https://fotodugnad.ra.no/photo/" + str(p.id)
                    first = False
                else:
                    or_clause += ",https://fotodugnad.ra.no/photo/" + str(p.id)
            if len(or_clause) > 4:
                response = json.loads(requests.get(
                    'https://graph.facebook.com/v2.3/?format=json&access_token=%s&%s' % (
                        APP_ID + '|' + settings.FACEBOOK_APP_SECRET, or_clause)).text)
                for k, v in response.items():
                    if 'og_object' in v:
                        photo_id = k.split('/')[-1]
                        photo = photos.get(pk=photo_id)
                        photo.fb_object_id = v['og_object']['id']
                        photo.light_save()
            start += 250
            end += 250
        # Now use the ids to request all comments from Facebook
        photos = Photo.objects.filter(fb_object_id__isnull=False)
        photo_count = photos.count()
        start = 0
        end = 250
        while start <= photo_count:
            ids = 'ids='
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
                response = json.loads(requests.get('https://graph.facebook.com/comments/?access_token=%s&%s' % (
                    APP_ID + '|' + settings.FACEBOOK_APP_SECRET, ids)).text)
                for k, v in response.items():
                    if 'data' in v:

                        for comment in v['data']:
                            existing_comment = PhotoComment.objects.filter(fb_comment_id=comment['id']).first()
                            if existing_comment:
                                existing_comment.text = comment['message']
                                existing_comment.save()
                            else:
                                object_id = comment['id'].split('_')[0]
                                new_photo_comment = PhotoComment(
                                    fb_comment_id=comment['id'],
                                    fb_user_id=comment['from']['id'],
                                    fb_object_id=object_id,
                                    text=comment['message'],
                                    created=comment['created_time'],
                                    photo=photos.get(fb_object_id=object_id)
                                )
                                new_photo_comment.save()
                        photo = Photo.objects.filter(fb_object_id=k).first()
                        photo.fb_comments_count = len(v['data'])
                        photo.first_comment = photo.comments.order_by('created').first().created
                        photo.latest_comment = photo.comments.order_by('created').last().created
                        photo.light_save()
            start += 250
            end += 250
