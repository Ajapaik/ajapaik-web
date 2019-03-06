import csv
import io
import os

from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album


class Command(BaseCommand):
    help = 'Will import new people from kreutzwaldi_sajand_people.csv'

    def handle(self, *args, **options):
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/kreutzwaldi_sajand_people.csv',
                     encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if row[0]:
                        # Previously confirmed already on Ajapaik
                        print('Skipped %s' % row[1])
                        continue
                    if row[3] or row[4]:
                        # Skip partial names or non-names
                        print('Skipped partial or non-name %s' % row[1])
                        continue
                    row[1] = row[1].strip()
                    existing_album = Album.objects.filter(name=row[1]).first()
                    if existing_album:
                        # Found existing person on Ajapaik, skip
                        print('Already on Ajapaik: %s' % row[1])
                        continue
                    new_person_album = Album(
                        name=row[1],
                        atype=Album.PERSON,
                        open=True,
                        gender=row[2],
                        wikidata_qid=row[6]
                    )
                    new_person_album.save()
                    print('Created %s' % new_person_album.name)
                    line_count += 1
            print(f'Processed {line_count} lines.')
