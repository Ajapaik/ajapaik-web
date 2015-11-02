from django.core.management.base import BaseCommand
from django.utils.timezone import now
from project.ajapaik.models import Points, AlbumPhoto


class Command(BaseCommand):
    help = 'Create album for mistakenly unlinked photos'

    def handle(self, *args, **options):
        album_id = 2531
        profile_id = 21914
        photo_ids = (
            29202, 29217, 29218, 29241, 29244, 29250, 29259, 29249, 29182, 29092, 29078, 29206, 29184, 29061, 29143, 29201,
            29116, 29199, 29056, 29029, 29190, 29256, 29097, 29236, 29177, 29185, 29104, 29117, 29172, 29074, 29096, 29247,
            29158, 29254, 29255, 29094, 29231, 29034, 29224, 29208, 29035, 29138, 29101, 29075, 29214, 29230, 29105, 29045,
            29198, 29248, 29246, 29227, 29243, 29233, 29188, 29120, 29047, 29162, 29228, 29212, 29067, 29142, 29150, 29258,
            29028, 29053, 29134, 29084, 29197, 29251, 29088, 29186, 29082, 29076, 29211, 29083, 29071, 29031, 29181, 29109,
            29090, 29087, 29099, 29229, 29129, 29055, 29086, 29059, 29178, 29033, 29171, 29136, 29260, 29062, 29130, 29110,
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
