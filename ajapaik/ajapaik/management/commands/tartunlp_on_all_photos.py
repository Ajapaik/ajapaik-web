from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Connects to TartuNLP socket server and retrieves neuro machine translations for empty description fields'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(
            Q(description_et__isnull=False)
            | Q(description_lv__isnull=False)
            | Q(description_lt__isnull=False)
            | Q(description_fi__isnull=False)
            | Q(description_ru__isnull=False)
            | Q(description_de__isnull=False)
            | Q(description_en__isnull=False)
        )
        for each in photos:
            print(f'Processing Photo {each.pk}')
            each: Photo
            each.fill_untranslated_fields()
