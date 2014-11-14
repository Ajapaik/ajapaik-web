import requests
import settings

query_url = "http://europeana.eu/api/v2/search.json"
resource_url = "http://europeana.eu/api/v2/record"

class BoundingBox(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class Search(object):
    def query(self, query_term, refinement_terms=None, bounding_box=None, start=1, size=12):
        qf_buf = []
        if bounding_box and isinstance(bounding_box, BoundingBox):
            query_term += " AND pl_wgs84_pos_lat[%s TO %s] AND pl_wgs84_pos_long[%s TO %s]" %(bounding_box.x1, bounding_box.x2, bounding_box.y1, bounding_box.y2)
        if refinement_terms:
            for t in refinement_terms.split(","):
                qf_buf.append("%s" %t)
        qf_buf.append("TYPE:IMAGE")
        arguments = {
            'wskey': settings.EUROPEANA_API_KEY,
            'query': query_term,
            'qf': qf_buf,
            'start': str(start),
            'rows': str(size),
            'profile': 'rich'
        }
        results = requests.get(query_url, params=arguments).json()

        item_count = int(results["itemsCount"])
        ret = []
        for i in xrange(0, item_count):
            if "edmIsShownBy" in results["items"][i]:
                ret.append(results["items"][i])

        return ret