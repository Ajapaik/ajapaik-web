from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from project.ajapaik.models import PhotoComment, MyXtdComment, Profile


class Command(BaseCommand):
    help = "Get all the FB comments, create django-comments-xtd comments, comments made by FB-only \
     (and not our local) users go under user 135188"

    def handle(self, *args, **options):
        fb_first_level_comments = PhotoComment.objects.filter(fb_comment_parent_id=0) \
            .order_by('-created')
        content_type_id = ContentType.objects.filter(app_label='ajapaik', model='photo').first().pk
        anonymous_profile = Profile.objects.filter(user_id=135188).get()
        for each in fb_first_level_comments:
            profile = Profile.objects.filter(fb_id=each.fb_user_id).first()
            if not profile:
                profile = anonymous_profile
            MyXtdComment(
                user=profile.user,
                level=0,
                followup=False,
                is_public=True,
                is_removed=False,
                comment=each.text,
                object_pk=each.photo_id,
                submit_date=each.created,
                facebook_comment_id=each.fb_comment_id,
                content_type_id=content_type_id,
                site_id=2
            ).save()
        # We only have first level comments in Fotodugnad
