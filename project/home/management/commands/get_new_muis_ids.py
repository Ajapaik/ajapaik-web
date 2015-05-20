from django.core.management.base import BaseCommand
import requests
from project import settings
from project.home.models import Photo
import ujson as json


class Command(BaseCommand):
    help = 'Curated results can now have a two-part ID, the museal and the picture representing it'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(muis_id__isnull=False)
        req_template = '{"method":"search","params":[{"fullSearch":{"value":"%s"},"id":{"value":"","type":"OR"},"what":{"value":""},"description":{"value":""},"who":{"value":""},"from":{"value":""},"number":{"value":""},"luceneQuery":null,"institutionTypes":["MUSEUM",null,null],"pageSize":200,"digital":true}],"id":0}'
        for p in photos:
            first_part = p.muis_id.split(':')[-1].split('_')[0]
            request_params = req_template % first_part
            response = requests.post(settings.AJAPAIK_VALIMIMOODUL_URL, data=request_params)
            result = json.loads(response.text)["result"]
            if len(result["ids"]) > 1:
                # TODO: Once Kaido gets us media IDs, set a totally unique identifier to all MUIS photos
                print result["ids"][0]
                print "------------------------------"