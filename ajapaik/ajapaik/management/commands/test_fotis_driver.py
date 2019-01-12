from django.core.management.base import BaseCommand

from ajapaik.ajapaik.curator_drivers.fotis import FotisDriver


class Command(BaseCommand):
    help = "Test FotisDriver"
    args = "search_term"

    def handle(self, *args, **options):
        fotis = FotisDriver()

        #print fotis.search({'fullSearch': args[0]})
