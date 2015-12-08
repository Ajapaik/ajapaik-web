from requests import post

from project.ajapaik.settings import AJAPAIK_VALIMIMOODUL_URL


class ValimimoodulDriver(object):
    def __init__(self):
        self.url = AJAPAIK_VALIMIMOODUL_URL

    def search(self, form):
        pass

    def get_by_ids(self, ids):
        ids_str = ['"' + each + '"' for each in ids]
        request_params = '{"method":"getRecords","params":[[%s]],"id":0}' % ','.join(ids_str)
        response = post(self.url, data=request_params)
        response.encoding = 'utf-8'

        return response