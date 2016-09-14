from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Do all the usual stuff'

    def handle(self, *args, **options):
        call_command('migrate', interactive=False)
        call_command('collectstatic', interactive=False)
        call_command('compress', force=True, interactive=False)
        # call_command('makemessages', all=True, interactive=False)
        # call_command('makemessages', all=True, domain='djangojs', interactive=False)
        # call_command('compilemessages', interactive=False)
