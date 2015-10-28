from django.core.management import BaseCommand
from project.ajapaik.models import Profile
from project.sift.models import CatTagPhoto, CatProfile, CatUserFavorite, CatPushDevice


class Command(BaseCommand):
    help = "Will create Sift.pics profiles from Ajapaik profiles"

    def handle(self, *args, **options):
        sift_tagging_user_ids = CatTagPhoto.objects.distinct('profile_id').values_list('profile_id', flat=True)
        sift_favoriting_user_ids = CatUserFavorite.objects.distinct('profile_id').values_list('profile_id', flat=True)
        sift_gcm_user_ids = CatPushDevice.objects.distinct('profile_id').values_list('profile_id', flat=True)
        all_ids = list(sift_tagging_user_ids) + list(sift_favoriting_user_ids) + list(sift_gcm_user_ids)
        ajapaik_profiles = Profile.objects.filter(pk__in=all_ids)
        for each in ajapaik_profiles:
            try:
                CatProfile(
                    user=each.user,
                ).save()
            except:
                pass