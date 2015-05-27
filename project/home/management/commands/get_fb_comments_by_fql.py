from django.core.management.base import BaseCommand
import requests
from project.home.facebook import APP_ID
from project.home.models import Photo, PhotoComment
from project.settings import FACEBOOK_APP_SECRET
import ujson as json


class Command(BaseCommand):
    help = 'Get all Facebook comments for our photos, mark earliest, latest and comment count'

    def handle(self, *args, **options):
        # First get the real FB ids for photos that don't have them in batches of 500
        photos = Photo.objects.filter(fb_object_id__isnull=True)
        photo_count = photos.count()
        start = 0
        end = 500
        while start < photo_count:
            or_clause = ''
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if first:
                    or_clause += "'http://ajapaik.ee/foto/" + str(p.id) + "/'"
                    first = False
                else:
                    or_clause += " OR url = 'http://ajapaik.ee/foto/" + str(p.id) + "/'"
            fql_string = "SELECT comments_fbid, url FROM link_stat WHERE url = %s limit 500" % or_clause
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
            start += 500
            end += 500

        # fql_string = "SELECT text, id, parent_id, fromid, time FROM comment WHERE object_id IN (SELECT comments_fbid FROM link_stat WHERE url = %s) ORDER BY time DESC limit 500" % or_clause
        # response = json.loads(requests.get('https://graph.facebook.com/fql?access_token=%s&q=%s' % (APP_ID + '|' + FACEBOOK_APP_SECRET, fql_string)).text)
        # print response
        # for each in response['data']:
            # existing_comment = PhotoComment.objects.filter(fb_comment_id=each['id']).first()
            # if existing_comment:
            #     existing_comment.text = each['text']
            #     existing_comment.save()
            # else:
            #     new_photo_comment = PhotoComment(
            #         fb_comment_id = each['id'],
            #         fb_user_id = each['fromid'],
            #         photo = photos.get(pk=)
            #     )
            # print each
            # print "-------------"

    #             photo = ForeignKey("Photo")
    # fb_comment_id = CharField(max_length=255, unique=True)
    # fb_comment_parent_id = CharField(max_length=255, blank=True, null=True)
    # fb_user_id = CharField(max_length=255)
    # text = TextField()
    # created = DateTimeField()