from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    args = 'user_id'
    help = 'Regenerates scores for rephotographers'

    def handle(self, *args, **options):
        user_id = None
        try:
            user_id = args[0]
        except IndexError:
            pass
        if user_id:
            photos = Photo.objects.filter(rephoto_of__isnull=False, user__pk=user_id)
        else:
            photos = Photo.objects.filter(rephoto_of__isnull=False, user__isnull=False).distinct('user')
        for p in photos:
            p.user.update_rephoto_score()
