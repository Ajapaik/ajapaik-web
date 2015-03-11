from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from project import settings
from project.home.models import Area, Album
from django.utils import translation

class Command(BaseCommand):
    help = "Take model translations from areas and apply to albums where possible"

    def handle(self, *args, **options):
        areas = Area.objects.all()
        for a in areas:
            translation.activate('et')
            try:
                matching_albums = Album.objects.filter(name=a.name)
                for ma in matching_albums:
                    for locale in settings.MODELTRANSLATION_LANGUAGES:
                        translation.activate(locale)
                        ma.name = a.name
                        ma.save()
            except ObjectDoesNotExist:
                continue