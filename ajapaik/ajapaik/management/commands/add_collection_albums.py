from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Source

class Command(BaseCommand):
    help = 'Add collection albums and assign each photo that has source to some album'

    def handle(self, *args, **options):
        photos =  Photo.objects.exclude(source__isnull)
        for photo in photos:
            sourceAlbum = Album.objects.filter(source_id=self.source_id).first()
            if sourceAlbum is None:
                sourceAlbum = Album(
                    name = self.source.name,
                    slug = self.source.name,
                    atype = Album.COLLECTION,
                    cover_photo = self,
                    source = self.source
                )
                sourceAlbum.save()
        sources = Source.objects().all()
        for source in sources:
            album = Album.objects.filter(source_id=source.id).first()
            if album is not None:
                album.set_calculated_fields()
                album.save()