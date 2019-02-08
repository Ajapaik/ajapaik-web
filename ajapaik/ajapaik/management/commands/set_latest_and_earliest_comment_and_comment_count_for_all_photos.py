from django.core.management.base import BaseCommand
from django.db.models import Count
from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Set latest and earliest comment, comment count for all photos'

    def handle(self, *args, **options):
        photos_with_comments_count = Photo.objects.filter(comments__isnull=False).count()
        start = 0
        while start < photos_with_comments_count:
            photos = Photo.objects.select_related('comments').annotate(my_comment_count=Count('comments'))[:start]
            for p in photos:
                p.comment_count = p.my_comment_count
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
            start += 50