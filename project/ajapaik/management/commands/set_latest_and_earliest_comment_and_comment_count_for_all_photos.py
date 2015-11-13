from django.core.management.base import BaseCommand
from django.db.models import Count
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Set latest and earliest comment, comment count for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.prefetch_related('comments').annotate(comment_count=Count('comments'))
        for p in photos:
            p.fb_comments_count = p.comment_count
            first_comment = p.comments.order_by('created').first()
            if first_comment:
                p.first_comment = first_comment.created
            else:
                p.first_comment = None
            latest_comment = p.comments.order_by('created').last()
            if latest_comment:
                p.latest_comment = latest_comment.created
            else:
                p.latest_comment = None
            p.light_save()