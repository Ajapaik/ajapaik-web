from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import ImageSimilarity, Photo

class Command(BaseCommand):
    help = "Set has similar flag for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(similar_photos__isnull=False)
        for photo in photos:
            try:
                results = ImageSimilarity.objects.filter(from_photo_id=photo.id).exclude(similarity_type=0)
                if results.count() > 0:
                    photo.hasSimilar = True
                else:
                    results = ImageSimilarity.objects.filter(to_photo_id=photo.id).exclude(similarity_type=0)
                    if results.count() > 0:
                        photo.hasSimilar = True
                    else:
                        photo.hasSimilar = False
                photo.save()
            except IndexError:
                photo_id = None