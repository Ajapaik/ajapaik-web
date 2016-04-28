# encoding: utf-8
from ujson import loads, dumps

from django.core.urlresolvers import reverse
from requests import post

from project.ajapaik.models import Photo, AlbumPhoto, Album
from project.ajapaik.settings import AJAPAIK_VALIMIMOODUL_URL, MEDIA_URL


class ValimimoodulDriver(object):
    def __init__(self):
        self.url = AJAPAIK_VALIMIMOODUL_URL

    def search(self, cleaned_data):
        institution_string = ''
        etera_string = ''
        if cleaned_data['useMUIS']:
            institution_string += '"MUSEUM"'
        else:
            institution_string += 'null'
        if cleaned_data['useDIGAR']:
            institution_string += ',"LIBRARY"'
        else:
            institution_string += ',null'
        if cleaned_data['useMKA']:
            institution_string += ',"ARCHIVE"'
        else:
            institution_string += ',null'
        if cleaned_data['useETERA']:
            etera_string = 'ETERA'
            institution_string = 'null,null,null'
        request_params = '{"method":"search","params":[{"fullSearch":{"value":"%s"},"id":{"value":"","type":"OR"},' \
                         '"what":{"value":""},"description":{"value":""},"who":{"value":""},"from":{"value":"%s"},' \
                         '"number":{"value":""},"luceneQuery":null,"institutionTypes":[%s],"pageSize":200,' \
                         '"digital":true}],"id":0}' % (cleaned_data['fullSearch'].encode('utf-8'), etera_string, institution_string)
        response = post(self.url, data=request_params)
        response.encoding = 'utf-8'

        return response

    def get_by_ids(self, ids):
        ids_str = ['"' + each + '"' for each in ids]
        request_params = '{"method":"getRecords","params":[[%s]],"id":0}' % ','.join(ids_str)
        response = post(self.url, data=request_params)
        response.encoding = 'utf-8'

        return response

    @staticmethod
    def transform_response(response, remove_existing=False):
        full_response_json = loads(response.text)
        result = loads(response.text)
        if 'result' in result:
            result = result['result']
            if 'firstRecordViews' in result:
                data = result['firstRecordViews']
            else:
                data = result
            check_dict = {}
            etera_second_image_remove_dict = {}
            for each in data:
                each['isETERASecondImage'] = False
                if each['collections'] == 'DIGAR':
                    current_id = each['imageUrl'].split('=')[-1]
                    each['imageUrl'] = MEDIA_URL + 'uploads/DIGAR_' + current_id + '_1.jpg'
                    each['identifyingNumber'] = current_id
                    each['urlToRecord'] = 'http://www.digar.ee/id/nlib-digar:' + current_id
                    each['institution'] = 'Rahvusraamatukogu'
                    each['keywords'] = each['description']
                    each['description'] = each['title']
                    existing_photo = Photo.objects.filter(source__description='Rahvusraamatukogu',
                                                          external_id=current_id).first()
                else:
                    parts = each['id'].split('_')
                    if each['institution'] == 'ETERA':
                        each['identifyingNumber'] = str(parts[0].split(':')[2])
                        if each['mediaOrder'] == 1:
                            each['isETERASecondImage'] = True
                            etera_second_image_remove_dict[each['id']] = True
                    existing_photo = Photo.objects.filter(external_id=parts[0]).first()
                if existing_photo:
                    each['ajapaikId'] = existing_photo.pk
                    check_dict[each['id']] = False
                    if not remove_existing:
                        album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                        each['albums'] = [[x[0], x[1]] for x in Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)\
                            .values_list('id', 'name')]
                        for e in each['albums']:
                            e[0] = reverse('project.ajapaik.views.frontpage') + '?album=' + str(e[0])
                else:
                    each['ajapaikId'] = False
                    check_dict[each['id']] = True

            if remove_existing:
                data = [x for x in data if not x['ajapaikId']]
                if 'firstRecordViews' in result:
                    full_response_json['result']['ids'] = [x for x in full_response_json['result']['ids']
                                                           if x not in check_dict or check_dict[x]]

            data = [x for x in data if not x['isETERASecondImage']]
            if 'firstRecordViews' in result:
                full_response_json['result']['ids'] = [x for x in full_response_json['result']['ids']
                                                       if x not in etera_second_image_remove_dict or not
                                                       etera_second_image_remove_dict[x]]
                data = sorted(data, key=lambda k: k['id'])
                full_response_json['result']['firstRecordViews'] = data

            response = dumps(full_response_json)

        return response