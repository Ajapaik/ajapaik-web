import codecs

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Get more stats for Vahur"

    def handle(self, *args, **options):
        f = codecs.open(
            f'{settings.ABSOLUTE_PROJECT_ROOT}/ajapaik/ajapaik/management/commands/photo_geotagged_week.txt', 'r',
            'utf-8')
        data = f.readlines()
        f.close()
        count_dict = {}
        for each in data:
            parts = each.split('\t')
            parts[0] = parts[0].strip()
            parts[1] = parts[1].strip()
            if parts[1] not in count_dict:
                count_dict[parts[1]] = 1
            else:
                count_dict[parts[1]] += 1
        f = codecs.open(
            settings.ABSOLUTE_PROJECT_ROOT +
            '/ajapaik/ajapaik/management/commands/results/photo_geotagged_week_parsed.txt', 'w', 'utf-8')
        for each in sorted(count_dict.items(), key=lambda key_value: key_value[0]):
            f.write(f'{each[0]}\t{str(each[1])}\n')
