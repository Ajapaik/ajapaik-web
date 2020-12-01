import datetime

from django.core.management import BaseCommand

from ajapaik.ajapaik.models import Profile


class Command(BaseCommand):
    help = 'Find and delete profiles/users that have no data attached (just people who have arrived ' \
           'at the page and never done anything)'

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(
            # Own fields
            first_name__isnull=True,
            last_name__isnull=True,

            fb_name__isnull=True,
            fb_link__isnull=True,
            fb_id__isnull=True,
            fb_token__isnull=True,
            fb_hometown__isnull=True,
            fb_current_location__isnull=True,
            fb_birthday__isnull=True,
            fb_email__isnull=True,
            fb_user_friends__isnull=True,

            google_plus_id__isnull=True,
            google_plus_email__isnull=True,
            google_plus_link__isnull=True,
            google_plus_name__isnull=True,
            google_plus_token__isnull=True,
            google_plus_picture__isnull=True,

            deletion_attempted__isnull=True,

            # Related model fields
            photos__isnull=True,
            albums__isnull=True,
            album_photo_links__isnull=True,
            datings__isnull=True,
            dating_confirmations__isnull=True,
            difficulty_feedbacks__isnull=True,
            geotags__isnull=True,
            points__isnull=True,
            skips__isnull=True,
            likes__isnull=True
        )

        start = 0
        end = 10000
        while end < 2000000:
            profiles_slice = profiles[start:end]
            for each in profiles_slice:
                try:
                    each.user.delete()
                except:  # noqa
                    each.deletion_attempted = datetime.datetime.now()
                    each.save()
            start += 10000
            end += 10000
