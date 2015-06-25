# encoding: utf-8
from django.core.management.base import BaseCommand
import requests
from project import settings
from project.home.models import Photo
import ujson as json


class Command(BaseCommand):
    help = 'Curated results can now have a two-part ID, the museal and the picture representing it'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(muis_id__isnull=False)
        req_template = u'{"method":"search","params":[{"fullSearch":{"value":"%s"},"id":{"value":"","type":"OR"},"what":{"value":""},"description":{"value":""},"who":{"value":""},"from":{"value":""},"number":{"value":"%s"},"luceneQuery":null,"institutionTypes":["MUSEUM",null,null],"pageSize":200,"digital":true}],"id":0}'
        for p in photos:
            first_part = p.muis_id.split(':')[-1].split('_')[0]
            request_params = req_template % (first_part, p.source_key)
            response = requests.post(settings.AJAPAIK_VALIMIMOODUL_URL, data=request_params.encode('utf-8'))
            result = json.loads(response.text)["result"]
            for each in result["firstRecordViews"]:
                if each["mediaOrder"] == 0 and first_part in each["id"]:
                    print "Old %s" % p.muis_id
                    print "New %s" % each["id"]
                    old_muis_id = p.muis_id
                    p.muis_id = each["id"].encode('utf-8')
                    p.light_save()
                    print "Updated %d muis_id %s -> %s" % (p.id, old_muis_id, p.muis_id)
                    break