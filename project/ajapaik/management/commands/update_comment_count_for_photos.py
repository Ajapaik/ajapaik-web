from django.core.management.base import BaseCommand

from project.ajapaik.models import Photo, MyXtdComment


class Command(BaseCommand):
    help = "Set first_comment, latest_comment, comment_count for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for p in photos:
            print p.pk
            comments = MyXtdComment.objects.filter(
                object_pk=p.pk, is_removed=False
            )
            first_comment = comments.order_by('-submit_date').first()
            latest_comment = comments.order_by('submit_date').first()
            p.first_comment = None
            p.latest_comment = None
            if first_comment:
                p.first_comment = first_comment.submit_date
            if latest_comment:
                p.latest_comment = latest_comment.submit_date
            p.comment_count = comments.count()

            p.light_save()