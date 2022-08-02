from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import User,  Photo,Licence
from ajapaik.ajapaik.mediawiki.mediawiki import wikimedia_whoami, upload_file_to_commons, get_wikimedia_api_client, get_random_commons_image, download_tmp_file, remove_tmp_file

class Command(BaseCommand):
    help = 'Fetch random photo from commons and uploads it'

    def handle(self, *args, **options):
        user = User.objects.filter(username="Zache-test").first()

        r=wikimedia_whoami(user)
        print(r.content)

        client=get_wikimedia_api_client(user)
        print(wikitext)

        image=get_random_commons_image(1)
        local_filename=download_tmp_file(image['image_url'])

        r=upload_file_to_commons(client, local_filename, image["title"], image["wikitext"], "uploading " + image['image_url'])
        print(r.content)
        remove_tmp_file(image["image_url"])
