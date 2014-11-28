import re,csv,hashlib,os.path,shutil
from django.core.management.base import BaseCommand,CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from project.models import Photo

class Command(BaseCommand):
    args='limit'
    help='Will generate a slug for every photo'
    
    def handle(self,*args,**options):
        limit = 10
        for photo in Photo.objects.filter(source_key__contains="_"):
            if photo.description is not None:
                desc = "%s-" % "-".join(slugify(photo.description).split('-')[:4])[:35]
            else:
                desc = ""
            
            slug = "%s%s_%s" % (desc, photo.source or "AJP", photo.source_key)
            photo.slug = slug
            print "Created: %s" % slug
            photo.save()
            
        