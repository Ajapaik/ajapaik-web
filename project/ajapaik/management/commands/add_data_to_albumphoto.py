from django.core.management.base import BaseCommand
from project.ajapaik.models import Points, Photo, AlbumPhoto


class Command(BaseCommand):
    help = 'Will determine user reference, type for AlbumPhotos connection table'

    def handle(self, *args, **options):
        points = Points.objects.filter(action=Points.PHOTO_CURATION)
        photos = Photo.objects.filter(pk__in=[x.photo_id for x in points])
        for p in photos:
            first_aps_for_curated_photo = AlbumPhoto.objects.filter(photo=p).order_by('created')[:2]
            AlbumPhoto.objects.filter(pk__in=[x.pk for x in first_aps_for_curated_photo]).update(profile=p.user, type=AlbumPhoto.CURATED)
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        for p in photos:
            photo_aps = AlbumPhoto.objects.filter(photo=p)
            photo_aps.update(profile=p.user)