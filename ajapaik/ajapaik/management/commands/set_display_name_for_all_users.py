from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import Profile


class Command(BaseCommand):
    help = "Will set display name for each non-anonymous user"

    def handle(self, *args, **options):
        profiles = Profile.objects.exclude(
            Q(first_name__isnull=True) & Q(last_name__isnull=True) & Q(google_plus_name__isnull=True) & Q(
                fb_name__isnull=True) & Q(google_plus_email__isnull=True))
        for profile in profiles:
            if profile.first_name and profile.last_name:
                profile.display_name = '%s %s' % (profile.first_name, profile.last_name)
            elif profile.google_plus_name:
                profile.display_name = profile.google_plus_name
            elif profile.fb_name:
                profile.display_name = profile.fb_name
            elif profile.google_plus_email:
                try:
                    profile.display_name = profile.google_plus_email.split('@')[0]
                except:  # noqa
                    pass
            elif profile.first_name:
                profile.display_name = profile.first_name
            elif profile.last_name:
                profile.display_name = profile.last_name
            profile.save()
