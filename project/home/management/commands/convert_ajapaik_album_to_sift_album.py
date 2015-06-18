from django.core.management.base import BaseCommand
from django.utils.translation import activate
from project.home.models import Album, CatAlbum, CatPhoto


class Command(BaseCommand):
    help = "Will create Sift.pics album from existing Ajapaik album"
    args = "ap_album_id"

    def handle(self, *args, **options):
        activate('et')
        ap_album_id = args[0]
        a = Album.objects.get(pk=ap_album_id)
        sa = CatAlbum(
            title = a.name.encode('utf-8'),
            subtitle = a.description.encode('utf-8'),
        )
        sa.save()
        for ap in a.photos.filter(rephoto_of__isnull=True):
            cp = CatPhoto(
                title = ap.description.encode('utf-8'),
                image = ap.image,
                author = ap.author.encode('utf-8'),
                source = ap.source,
                source_url = ap.source_url,
                source_key = ap.source_key.encode('utf-8'),
            )
            cp.save()
            sa.photos.add(cp)
        sa.image = sa.photos.order_by('?').first().image
        sa.save()