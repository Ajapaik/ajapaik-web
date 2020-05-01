# encoding: utf-8 
from django.core.management.base import BaseCommand 
from ajapaik.ajapaik.models import Album, Photo 
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle 

class Command(BaseCommand):
    help = "Resets gender of face annotations, that are shown as 'unsure'" 
    def handle(self, *args, **options):
        rectangles = FaceRecognitionRectangle.objects.exclude(subject_consensus__isnull=True).filter(gender__gte=2)
        for rectangle in rectangles: 
            album = Album.objects.filter(id=rectangle.subject_consensus.id).first()
            if(album.gender is not None and rectangle.gender is not None):
                if(album.gender==0):
                    rectangle.gender = 1
                    rectangle.save() 
                if(album.gender==1):
                    rectangle.gender = 0 
                    rectangle.save() 