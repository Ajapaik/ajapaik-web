from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from project.ajapaik.models import Tour


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_tour(request, id):
    tour = Tour.objects.filter(pk=id).first()
    ret = {
        'photos': [],
    }
    if tour:
        for p in tour.photos.order_by('tourphoto__order'):
            ret['photos'].append({
                'name': p.description,
                'lat': p.lat,
                'lng': p.lon,
                'azimuth': p.azimuth
            })

    return Response(ret)
