# encoding: utf-8
from json import loads
from django.core.management.base import BaseCommand
from django.utils.translation import activate
import requests
from project.ajapaik import settings
from project.ajapaik.models import Photo, PhotoMetadataUpdate


class Command(BaseCommand):
    help = "Will run on the 2nd and 16th (Valimimoodul updates on the 1st and 15th) to check for metadata updates"

    def handle(self, *args, **options):
        activate('et')
        photos_with_muis_id = Photo.objects.filter(external_id__isnull=False)
        photo_dict = {p.external_id: p for p in photos_with_muis_id}
        photo_count = len(photo_dict)
        start = 0
        end = 500
        while start <= photo_count:
            id_or_clause = ''
            for k, v in photo_dict.items()[start:end]:
                id_or_clause += k.split(':')[-1] + ' '
            valimimoodul_request_str = '{"method":"search","params":[{"fullSearch":{"value":""},"id":{"value":"%s","type":"OR"},"what":{"value":""},"description":{"value":""},"who":{"value":""},"from":{"value":""},"number":{"value":""},"luceneQuery":null,"institutionTypes":["MUSEUM",null,null],"pageSize":200,"digital":true}],"id":0}' % id_or_clause
            response = requests.post(settings.AJAPAIK_VALIMIMOODUL_URL, data=valimimoodul_request_str)
            result = loads(response.text.encode('utf-8'))['result']['firstRecordViews']
            for each in result:
                existing = photo_dict[each['id']]
                existing_desc = None
                existing_author = None
                new_desc = each['title'].encode('utf-8').replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').replace(' ,', ',').strip()
                new_author = each['creators'].encode('utf-8').replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').replace(' ,', ',').strip()
                log_object = PhotoMetadataUpdate(
                    photo=existing
                )
                if existing.description:
                    existing_desc = existing.description.encode('utf-8')
                if new_desc != '' and new_desc != existing_desc:
                    log_object.old_description = existing_desc
                    log_object.new_description = new_desc
                    log_object.save()
                    existing.description = new_desc
                    existing.light_save()
                if existing.author:
                    existing_author = existing.author.encode('utf-8')
                if new_author != '' and new_author != existing_author:
                    log_object.old_author = existing_author
                    log_object.new_author = new_author
                    log_object.save()
                    existing.author = new_author
                    existing.light_save()
            start += 500
            end += 500