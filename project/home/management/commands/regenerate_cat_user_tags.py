import json
from django.core.management.base import BaseCommand
from project.home.models import Profile, CatTagPhoto
from project.settings import ABSOLUTE_PROJECT_ROOT


class Command(BaseCommand):
    help = "Will copy over categorizer user tags from staging"

    def handle(self, *args, **options):
        data = json.loads(open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/cattags.json', 'r').read())
        for each in data:
            corresponding_profile = Profile.objects.get(user__username=each["username"])
            CatTagPhoto(
                created=each["created"],
                modified=each["modified"],
                album_id=each["album_id"],
                photo_id=each["photo_id"],
                tag_id=each["tag_id"],
                value=each["value"],
                profile_id=corresponding_profile.user_id
            ).save()