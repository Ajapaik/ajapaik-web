import csv
import io
import os

from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


# TODO: Can remove
class Command(BaseCommand):
    help = 'Will set Wikidata QID for some of our person albums'

    def handle(self, *args, **options):
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/qids.csv',
                     encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            for row in csv_reader:
                album = Album.objects.filter(pk=row[1]).get()
                album.wikidata_qid = row[0]
                album.save()
                line_count += 1
            print(f'Processed {line_count} lines.')
