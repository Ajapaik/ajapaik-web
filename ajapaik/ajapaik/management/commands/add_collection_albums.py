from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Source

class Command(BaseCommand):
    help = 'Add collection albums and assign each photo that has source to some album'

    def handle(self, *args, **options):
        photos =  Photo.objects.exclude(source_id__isnull=True)
        for photo in photos:
            sourceAlbum = Album.objects.filter(source_id=photo.source_id).first()
            if sourceAlbum is None:
                sourceAlbum = Album(
                    name = photo.source.name,
                    slug = photo.source.name,
                    atype = Album.COLLECTION,
                    cover_photo = photo,
                    source = photo.source
                )
                sourceAlbum.save()
            AlbumPhoto(
                type=AlbumPhoto.COLLECTION,
                photo=photo,
                album=sourceAlbum
            ).save()
        sources = Source.objects().all()
        for source in sources:
            album = Album.objects.filter(source=source).first()
            if album is not None:
                album.set_calculated_fields()
                album.save()