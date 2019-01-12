from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Profile


class Command(BaseCommand):
    help = "Will run set_calculated_fields and save for one or every profile"
    args = "profile_id"

    def handle(self, *args, **options):
        profile_id = None
        try:
            profile_id = args[0]
        except IndexError:
            pass
        if profile_id is not None:
            profile = Profile.objects.get(user_id=profile_id)
            profile.set_calculated_fields()
            profile.save()
        else:
            for profile in Profile.objects.all():
                #print profile.id
                profile.set_calculated_fields()
                profile.save()