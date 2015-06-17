# encoding: utf-8
from django.core.management.base import BaseCommand
from django.utils.translation import activate
from project.home.models import Photo


class Command(BaseCommand):
    help = "Restores photo metadata to old form from our history table"

    def handle(self, *args, **options):
        activate('et')
        photos_with_muis_id = Photo.objects.filter(muis_id__isnull=False).prefetch_related('metadata_updates')
        for p in photos_with_muis_id:
            for mu in p.metadata_updates.order_by('-created'):
                if mu.old_description:
                    p.description = mu.old_description.encode('utf-8')
                if mu.old_author:
                    p.author = mu.old_author
                p.light_save()
            p.metadata_updates.all().delete()