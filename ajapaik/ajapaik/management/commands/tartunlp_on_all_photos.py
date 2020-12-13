from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Connects to TartuNLP API and retrieves neuro machine translations for empty description fields'

    def add_arguments(self, parser):
        parser.add_argument('number_of_photos', nargs='+', type=int, help='Batch size')

    # TODO: Use event loop?
    # event_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(event_loop)
    # tasks = [
    #     asyncio.ensure_future(
    #         self.get_single(each)
    #     ) for each in photos
    # ]
    # done, _ = event_loop.run_until_complete(asyncio.wait(tasks))
    # event_loop.close()
    def handle(self, *args, **options):
        batch_size = options['number_of_photos'][0]
        if batch_size:
            photos = Photo.objects.exclude(description_et__isnull=False, description_lv__isnull=False,
                                           description_lt__isnull=False, description_fi__isnull=False,
                                           description_ru__isnull=False, description_de__isnull=False,
                                           description_en__isnull=False).filter(
                Q(description_et__isnull=False)
                | Q(description_lv__isnull=False)
                | Q(description_lt__isnull=False)
                | Q(description_fi__isnull=False)
                | Q(description_ru__isnull=False)
                | Q(description_de__isnull=False)
                | Q(description_en__isnull=False)
            )
            for each in photos[:batch_size]:
                print(f'Processing Photo {each.pk}')
                each: Photo
                each.fill_untranslated_fields()
