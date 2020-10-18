from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import AlbumPhoto, Points, PhotoViewpointElevationSuggestion


class Command(BaseCommand):
    help = "Add viewpoint elevation suggestions aerophotography albums"

    def handle(self, *args, **options):
        album_photos = AlbumPhoto.objects.filter(album_id=18893)
        for album_photo in album_photos:
            if album_photo.profile:
                new_suggestion = PhotoViewpointElevationSuggestion(proposer=album_photo.profile, photo=album_photo.photo, viewpoint_elevation=2, created=album_photo.created)
                new_suggestion.save()
                album_photo.photo.viewpoint_elevation = 2
                album_photo.photo.save()
                Points(user=album_photo.profile, action=Points.ADD_VIEWPOINT_ELEVATION, photo=album_photo.photo, points=20,created=album_photo.created).save()