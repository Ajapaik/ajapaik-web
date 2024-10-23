import logging
import traceback
import urllib
import xml.etree.ElementTree as ET

import requests
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo, ApplicationException


class Command(BaseCommand):
    help = 'Import photos from MUIS set'

    def add_arguments(self, parser):
        parser.add_argument(
            'photo_ids', nargs='+', type=int,
            help='Photo ids, where to import the photos from muis'
        )

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        photo_ids = (options['photo_ids'])
        if not photo_ids:
            logger.info("Please add photo ids that you want to update")

        photos = Photo.objects.filter(id__in=photo_ids)
        muis_url = 'https://www.muis.ee/OAIService/OAIService'

        for photo in photos:
            list_identifiers_url = f'{muis_url}?verb=GetRecord&identifier={photo.external_id}&metadataPrefix=lido'
            url_response = urllib.request.urlopen(list_identifiers_url)

            ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}
            record = 'd:metadata/lido:lidoWrap/lido:lido/'
            resource_wrap = f'{record}lido:administrativeMetadata/lido:resourceWrap/'

            read_url = url_response.read()
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.fromstring(read_url, parser=parser)
            rec = tree.find('d:GetRecord/d:record', ns)

            try:
                rp_lr = 'resourceRepresentation/lido:linkResource'
                link_resource_record = rec.find(f'{resource_wrap}lido:resourceSet/lido:{rp_lr}', ns)

                if link_resource_record is None:
                    logger.info(f"Skipping {photo.external_id}, as there is no image resource")
                    continue

                image_url = link_resource_record.text

                if link_resource_record is not None:
                    image_extension = (link_resource_record.attrib['{' + ns['lido'] + '}formatResource']).lower()
                else:
                    logger.info(f"Skipping {photo.external_id}, as there is not image extension specified")
                    continue

                if not image_url or image_extension not in ['gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp']:
                    logger.info(f"Skipping {photo.external_id}, as there are no photos which are supported")
                    continue

                response = requests.get(image_url)
                if response.status_code != 200:
                    logger.info(f"Skipping {photo.external_id}, as we did not get a valid response when downloading")

                img_data = response.content
                with open(photo.image.name, 'wb') as handler:
                    handler.write(img_data)

                photo.set_calculated_fields()
            except Exception as e:
                logger.exception(e)
                exception = ApplicationException(exception=traceback.format_exc(), photo=photo)
                exception.save()
