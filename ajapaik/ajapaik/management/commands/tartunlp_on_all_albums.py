from django.core.management.base import BaseCommand
from django.db.models import Q, QuerySet

from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik.utils import fill_untranslated_fields


class Command(BaseCommand):
    help = 'Connects to TartuNLP API and retrieves neuro machine translations for empty name fields'

    def handle(self, *args, **options):
        albums: QuerySet[Album] = Album.objects.exclude(
            Q(atype=Album.AUTO) |
            Q(name_original_language__isnull=False) |
            Q(atype=Album.PERSON) |
            Q(atype=Album.COLLECTION)
        ).filter(
            Q(name_et__isnull=False)
            | Q(name_lv__isnull=False)
            | Q(name_lt__isnull=False)
            | Q(name_fi__isnull=False)
            | Q(name_ru__isnull=False)
            | Q(name_de__isnull=False)
            | Q(name_en__isnull=False)
        )
        for each in albums:
            print(f'Processing Album {each.pk}')
            fill_untranslated_fields(each, 'name')
