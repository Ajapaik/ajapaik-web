import requests
from ajapaik.ajapaik.facebook import APP_ID
from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo, PhotoComment


class Command(BaseCommand):
    help = 'Get all Facebook comments for our photos'

    def handle(self, *args, **options):
        # First get the real FB ids for photos that don't have them in batches of 50
        fb_graph_url = 'https://graph.facebook.com'
        access_token = f'{APP_ID}|{settings.FACEBOOK_APP_SECRET}'
        photos = Photo.objects.filter(fb_object_id__isnull=True)
        photo_count = photos.count()
        start = 0
        end = 50
        while start <= photo_count:
            # TODO: Make it nicer using map and join
            or_clause = 'ids='
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if first:
                    or_clause += f'https://ajapaik.ee/photo/{str(p.id)}/'
                    first = False
                else:
                    or_clause += f',https://ajapaik.ee/photo/{str(p.id)}/'
            if len(or_clause) > 4:
                response = requests.get(
                    f'{fb_graph_url}/v7.0/?format=json&access_token={access_token}&%{or_clause}').json()

                for k, v in response.items():
                    if 'og_object' in v:
                        photo_id = k.split('/')[-2]
                        photo = photos.get(pk=photo_id)
                        photo.fb_object_id = v['og_object']['id']
                        photo.light_save()
            start += 50
            end += 50
        # Now use the ids to request all comments from Facebook
        photos = Photo.objects.filter(fb_object_id__isnull=False)
        photo_count = photos.count()
        start = 0
        end = 50
        while start <= photo_count:
            # TODO: Use map and/or join here instead of for loops
            ids = 'ids='
            photo_batch = photos[start:end]
            first = True
            for p in photo_batch:
                if len(p.fb_object_id) > 0:
                    if first:
                        ids += str(p.fb_object_id)
                        first = False
                    else:
                        ids += f',{str(p.fb_object_id)}'
            if len(ids) > 0:
                response = requests.get(f'{fb_graph_url}/comments/?access_token=%{access_token}&%{ids}').json()
                for k, v in response.items():
                    if 'data' in v:
                        for comment in v['data']:
                            if existing_comment := PhotoComment.objects.filter(fb_comment_id=comment['id']).first():
                                existing_comment.text = comment['message']
                                existing_comment.save(update_fields=['message'])
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
                        first_comment = photo.comments.order_by('created').first()
                        if first_comment:
                            photo.first_comment = first_comment.created
                        latest_comment = photo.comments.order_by('created').last()
                        if latest_comment:
                            photo.latest_comment = latest_comment.created
                        photo.light_save()
                        for each in photo.albums.all():
                            each.comments_count_with_subalbums = each.get_comment_count_with_subalbums()
                            each.light_save()
            start += 50
            end += 50
