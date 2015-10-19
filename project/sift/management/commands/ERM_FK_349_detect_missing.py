from django.core.management.base import BaseCommand
from project.sift.models import CatPhoto
from project.sift.settings import ABSOLUTE_PROJECT_ROOT
from ujson import loads


class Command(BaseCommand):
    help = 'Find out which photos are missing from our database'

    def handle(self, *args, **options):
        with open(ABSOLUTE_PROJECT_ROOT + '/project/sift/management/commands/ERM_FK_349_response.json', 'r') as f:
            content = f.read()
        results = loads(content)['result']['firstRecordViews']
        missing = {x['identifyingNumber']: x['id'] for x in results if x['identifyingNumber'].startswith('ERM Fk 349')}
        db_photo_keys = CatPhoto.objects.filter(album__pk=5).values_list('source_key', flat=True)
        for result in results:
            if result['identifyingNumber'] in db_photo_keys:
                if result['identifyingNumber'] in missing:
                    del(missing[result['identifyingNumber']])
        missing = missing.values()
        missing = [x.split(':')[2] for x in missing]
        print missing
        print len(missing)
        print '+'.join(missing)
