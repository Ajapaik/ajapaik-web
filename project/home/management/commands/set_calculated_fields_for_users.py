from django.core.management.base import BaseCommand
from project.home.models import Profile


class Command(BaseCommand):
    help = "Will run set_calculated_fields for every profile"
    args = "profile_id"

    def handle(self, *args, **options):
        profile_id = args[0]
        if profile_id:
            profile = Profile.objects.get(user_id=profile_id)
            profile.set_calculated_fields()
            profile.save()
        else:
            for profile in Profile.objects.all():
                print profile.id
                profile.set_calculated_fields()
                profile.save()