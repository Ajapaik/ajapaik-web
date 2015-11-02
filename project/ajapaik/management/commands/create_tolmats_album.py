from django.core.management.base import BaseCommand
from django.utils.timezone import now
from project.ajapaik.models import Points, AlbumPhoto


class Command(BaseCommand):
    help = 'Create album for mistakenly unlinked photos'

    def handle(self, *args, **options):
        album_id = 2513
        profile_id = 21914
        photo_ids = (
            29062, 29130, 29110,
            29041, 29252, 29160, 29242, 29030, 29187, 29245, 29032, 29253, 29058, 29100, 29159, 29173, 29127, 29169, 29257,
            29170
        )
        for pi in photo_ids:
            AlbumPhoto(
                album_id=album_id,
                photo_id=pi,
                profile_id=profile_id,
                type=AlbumPhoto.CURATED
            ).save()
            Points(
                user_id=profile_id,
                action=Points.PHOTO_CURATION,
                photo_id=pi,
                album_id=album_id,
                points=50,
                created=now()
            ).save()
