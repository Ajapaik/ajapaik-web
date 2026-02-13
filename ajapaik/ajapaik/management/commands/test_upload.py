from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import User
#from ajapaik.ajapaik.wikitext import  upload_own_photo_wikitext
from ajapaik.ajapaik.mediawiki.mediawiki import upload_file_to_commons, get_random_commons_image, download_tmp_file, remove_tmp_file, get_wikimedia_api_client
from requests import get
import json
import re

class Command(BaseCommand):
    help = 'Tests how OAUTH2 refresh_token works'


    def get_img_url(p,size=''):
        if 'imagesExtended' in p and len(p['imagesExtended']):
            if 'highResolution' in p['imagesExtended'][0]:
                if 'original' in p['imagesExtended'][0]['highResolution']:
                    t=p['imagesExtended'][0]['highResolution']
                    file_extension=t['format']
                    file_url=t['url']
                    print(file_extension)
            elif 'urls' in p['imagesExtended'][0]:
                sizes = [size, 'master', 'original', 'large', 'medium', 'small'];
                for s in sizes:
                    if s in p['imagesExtended'][0]['urls']:
                        if p['imagesExtended'][0]['urls'][s].startswith('/'):
                            return 'https://api.finna.fi' + p['imagesExtended'][0]['urls'][s]
                        else:
                            return p['imagesExtended'][0]['urls'][s]

        if 'images' in p and len(p['images']):
            return 'https://api.finna.fi' + p['images'][0]
        else:
            return None


    def get_finna_image(self, id):
        record_url = 'https://api.finna.fi/v1/record'
        finna_result = get(record_url, {
            'id': id,   
            'field[]': ['id', 'title', 'shortTitle', 'images', 'imageRights', 'authors', 'source', 'geoLocations', 'buildings',
                    'recordPage', 'year',
                    'summary', 'rawData', 'imagesExtended'],
        })

        results = finna_result.json()

        p = results.get('records', None)

        if p and p[0]:
            p = p[0]
            comma = ', '

            if not len(p['images']):
                return None

            institution = None
            if p['source']:
                if 'translated' in p['source'][0]:
                    institution = p['source'][0]['translated']
                elif 'value' in p['source'][0]:
                    institution = p['source'][0]['value']

            geography = None
            if 'geoLocations' in p:
                for each in p['geoLocations']:
                    if 'POINT' in each:
                        point_parts = each.split(' ')
                        lon = point_parts[0][6:]
                        lat = point_parts[1][:-1]
                        try:
                            p['longitude'] = float(lon)
                            p['latitude'] = float(lat)
                            geography = Point(x=float(lon), y=float(lat), srid=4326)
                            break
                        except Exception as e:
                            print(e)
                            continue

            title = p.get('title').rstrip()

            summary = ''
            if 'summary' in p:
                for each in p['summary']:
                    if len(each.rstrip()) > len(summary):
                        summary = re.sub(
                            '--[^-]*?(filmi|paperi|negatiivi|digitaalinen|dng|dia|lasi|väri|tif|jpg|, mv)[^-]*?$', '',
                            each).rstrip()

            if title in summary:
                description = summary
            elif len(title) < 20:
                description = f'{title}; {summary}'
            else:
                description = title

            if 'imageRights' in p and 'copyright' in p['imageRights']:
                licence_str = p['imageRights']['copyright']
                licence_description = p['imageRights']['description']
                licence_link = p['imageRights']['link']

            authors = []
            if 'authors' in p:
                if p['authors']['primary']:
                    for k, each in p['authors']['primary'].items():
                        authors.append(k)

            buildings = []
            if 'buildings' in p:
                if p['buildings']:
                    for k, each in p['buildings']:
                        buildings.append(p['buildings'][k])


            if 1:
                print(json.dumps(buildings, indent=4, sort_keys=True))
                exit(1)




    def handle(self, *args, **options):

        # user: 44387121 = Kimmo
        # user: 47476736 = Zache
        user = User.objects.filter(pk=47476736).first()
        print(user.first_name, user.last_name)
        client=get_wikimedia_api_client(user)
        source_file=get_random_commons_image(1)

        print(source_file)
        self.get_finna_image('museovirasto.6A357F809181D5780CB80319D69EAFEE')

        if 1:
            exit();

        filename=downloadFile(source_file["image_url"])

#        mediawiki_api_url="https://commons.wikimedia.org/w/api.php";
        REMOTENAME=source_file["title"]
        FILENAME=filename
        USER_AGENT="Ajapaik.ee OAUTH2 Uploader"
        COMMENT='Uploading test file from ' + source_file["description_url"]

        out={}
        out["licence"]="CC-BY-4.0"
        out["title"]="eläinsymboleilla koristeltuja hautaristejä Suistamon uudella hautausmaalla"
        out["description"]='sisällön kuvaus: kuvakortin kuvateksti: "Suistamo. Uusi hautausmaa. Kolme hautaristiä, joiden huipussa puinen linnunkuva [kaksi havainnepiirrosta]."'
        out["author"]="Hirsjärvi, Auvo"
        out["date"]="1935"
        out["place"]="Suistamo"
        out["institution"]=""
        out["year_category"]="[[Category:1935 in Finland]]"
        out["source"]="Museovirasto / Kansatieteen kuvakokoelma / KK1899:226, [https://finna.fi/Record/museovirasto.401434B5E8A5260A8D26D15C0282B0D4 museovirasto.401434B5E8A5260A8D26D15C0282B0D4]"
        out["identifierString"]="KK1899:226"
        out["footer_template"]=""
#        WIKITEXT=upload_own_photo_wikitext(out)
#
#        WIKITEXT=source_file["wikitext"]
#
#        r=upload_file_to_commons(client, FILENAME, REMOTENAME, WIKITEXT, COMMENT)
#        print(r.content)
#        client.close()
#        removeFile(source_file["image_url"])
