from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import AlbumPhoto, Points, PhotoSceneSuggestion


class Command(BaseCommand):
    help = "Add scene suggestions from interior photos album"

    def handle(self, *args, **options):
        album_photos = AlbumPhoto.objects.filter(album_id=11891)
        for album_photo in album_photos:
            if album_photo.profile:
                new_suggestion = PhotoSceneSuggestion(proposer=album_photo.profile, photo=album_photo.photo, scene=0, created=album_photo.created)
                new_suggestion.save()
                album_photo.photo.scene = 0
                album_photo.photo.save()
                Points(user=album_photo.profile, action=Points.CATEGORIZE_SCENE, photo=album_photo.photo, points=20,created=album_photo.created).save()