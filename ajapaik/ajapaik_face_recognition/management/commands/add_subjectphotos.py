from django.core.management.base import BaseCommand
from ajapaik import settings
from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle

from PIL import Image 

class Command(BaseCommand):
    def handle(self, *args, **options):
        rectangles = FaceRecognitionRectangle.objects.all()
        for rectangle in rectangles:
            p = Photo.objects.get(pk=rectangle.photo.id)
            if p.image is None:
                break
            path = settings.MEDIA_ROOT + "/" + str(p.image)
            image = Image.open(path)
            if image is not None:
                subjectCoordinates = rectangle.decode_coordinates()
                image_crop = image.crop((subjectCoordinates[3],subjectCoordinates[0],subjectCoordinates[1],subjectCoordinates[2]))
                subjectPhotoPath = settings.MEDIA_ROOT + "/portraits/" + str(rectangle.id) + '.jpg'
                image_crop.save(subjectPhotoPath, quality=95)
                rectangle.subjectPhoto = subjectPhotoPath
                rectangle.save()
            image.close()