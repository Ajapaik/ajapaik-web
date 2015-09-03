from django.core.management import BaseCommand
from project.ajapaik.models import Profile
from project.sift.models import CatTagPhoto, CatProfile


class Command(BaseCommand):
    help = "Will create Sift.pics profiles from Ajapaik profiles"

    def handle(self, *args, **options):
        sift_tagging_user_ids = CatTagPhoto.objects.distinct('profile_id').values_list('profile_id', flat=True)
        ajapaik_profiles = Profile.objects.filter(pk__in=sift_tagging_user_ids)
        for each in ajapaik_profiles:
            CatProfile(
                user=each.user,
            ).save()