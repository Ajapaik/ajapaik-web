from django.core.management.base import BaseCommand
from project.ajapaik.models import Points, Photo, AlbumPhoto


class Command(BaseCommand):
    help = 'Will find photos that have curating points attached, but are missing the implied 2 references'

    def handle(self, *args, **options):
        points = Points.objects.filter(action=Points.PHOTO_CURATION)
        photos = Photo.objects.filter(pk__in=[x.photo_id for x in points])
        erroneous_ids = []
        for p in photos:
            aps_for_curated_photo = AlbumPhoto.objects.filter(photo=p)
            if len(aps_for_curated_photo) < 2:
                erroneous_ids.append(p.id)
        print erroneous_ids