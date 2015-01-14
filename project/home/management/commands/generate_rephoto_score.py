from django.core.management.base import BaseCommand
from project.home.models import Photo

class Command(BaseCommand):
    args = 'user_id'
    help = 'Regenerates scores for rephotographers'

    def handle(self, *args, **options):
        args = list(args)
        user_id = None
        if len(args):
            user_id = args.pop(0)

        if user_id:
            rephoto_uploaders = Photo.objects.filter(rephoto_of__isnull=False, user__pk=user_id)[:1]
        else:
            rephoto_uploaders = Photo.objects.filter(rephoto_of__isnull=False, user__isnull=False).order_by('user').distinct('user')
        for u in rephoto_uploaders:
            u.user.update_rephoto_score()
            print >> self.stdout, (u.user.pk, u.user.fb_name, u.user.score_rephoto)