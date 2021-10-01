from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo, Transcription


class Command(BaseCommand):
    help = 'Calculate transcription counts and add dates'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for photo in photos:
            try:
                transcriptions = Transcription.objects.all().filter(photo__id=photo.id)
                if transcriptions.exists():
                    first_transcription = transcriptions.order_by('created').first()
                    last_transcription = transcriptions.order_by('-modified').first()
                    if first_transcription:
                        photo.first_transcription = first_transcription.created
                    if last_transcription:
                        photo.latest_transcription = last_transcription.modified
                    photo.transcription_count = transcriptions.count()
                    photo.light_save()
            except Exception:
                continue
