import json
from django.core.management.base import BaseCommand
from project.home.models import Profile, CatUserFavorite
from project.settings import ABSOLUTE_PROJECT_ROOT


class Command(BaseCommand):
    help = "Will copy over categorizer favorites from staging"

    def handle(self, *args, **options):
        data = json.loads(open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/catfavorites.json', 'r').read())
        for each in data:
            corresponding_profile = Profile.objects.get(user__username=each["username"])
            CatUserFavorite(
                created=each["created"],
                modified=each["modified"],
                album_id=each["album_id"],
                photo_id=each["photo_id"],
                profile_id=corresponding_profile.user_id
            ).save()