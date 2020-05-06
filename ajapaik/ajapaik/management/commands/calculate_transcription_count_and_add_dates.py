from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Photo, Transcription

class Command(BaseCommand):
    help = 'Calculate transcription counts and add dates'

    def handle(self, *args, **options):
        photos =  Photo.objects.all().filter(perceptual_hash__isnull=True)
        for photo in photos:
            try:
                transcriptions = Transcription.objects.all().filter(photo__id=photo.id)
                if transcriptions.count() > 0:
                    firstTranscription = transcriptions.order_by('created').first()
                    lastTranscription = transcriptions.order_by('-modified').first()
                    if firstTranscription:
                        photo.first_transcription = firstTranscription.created
                    if lastTranscription:
                        photo.last_transcription = firstTranscription.lastTranscription
                    photo.transcription_count = transcriptions.count()
            except Exception:
                continue
