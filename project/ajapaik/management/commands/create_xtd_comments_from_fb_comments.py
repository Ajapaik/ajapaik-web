from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from project.ajapaik.models import PhotoComment, MyXtdComment, Profile


class Command(BaseCommand):
    help = "Get all the FB comments, create django-comments-xtd comments"

    def handle(self, *args, **options):
        fb_first_level_comments = PhotoComment.objects.filter(fb_comment_parent_id=0).order_by('-created')
        content_type_id = ContentType.objects.filter(app_label='ajapaik', model='photo').first().pk
        for each in fb_first_level_comments:
            ajapaik_user = Profile.objects.filter(fb_id=each.fb_user_id).first()
            if ajapaik_user:
                MyXtdComment(
                    user=ajapaik_user.user,
                    level=0,
                    followup=False,
                    is_public=True,
                    is_removed=False,
                    comment=each.text,
                    object_pk=each.photo_id,
                    submit_date=each.created,
                    facebook_comment_id=each.fb_comment_id,
                    content_type_id=content_type_id,
                    site_id=1
                ).save()
        fb_non_first_level_comments = PhotoComment.objects.exclude(fb_comment_parent_id=0).order_by('-created')
        for each in fb_non_first_level_comments:
            ajapaik_user = Profile.objects.filter(fb_id=each.fb_user_id).first()
            parent_comment = MyXtdComment.objects.filter(facebook_comment_id=each.fb_comment_parent_id).first()
            if ajapaik_user and parent_comment:
                MyXtdComment(
                    user=ajapaik_user.user,
                    level=1,
                    followup=False,
                    is_public=True,
                    is_removed=False,
                    comment=each.text,
                    object_pk=each.photo_id,
                    submit_date=each.created,
                    content_type_id=content_type_id,
                    facebook_comment_id=each.fb_comment_id,
                    # 1 is ajapaik.ee
                    site_id=1,
                    parent_id=parent_comment.pk
                ).save()
