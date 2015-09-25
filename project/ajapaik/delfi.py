from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from project.ajapaik.forms import DelfiBboxRequestForm
from project.ajapaik.models import Photo
from project.ajapaik.serializers import DelfiBboxResponseSerializer


@api_view(['GET'])
@permission_classes((AllowAny,))
def photos_bbox(request):
    form = DelfiBboxRequestForm(request.query_params)
    if form.is_valid():
        qs = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False,
                                  lat__gte=form.cleaned_data['top_left'].y,
                                  lon__gte=form.cleaned_data['top_left'].x,
                                  lat__lte=form.cleaned_data['bottom_right'].y,
                                  lon__lte=form.cleaned_data['bottom_right'].x
        )
        photo_serializer = DelfiBboxResponseSerializer(qs, many=True)

        return Response(photo_serializer.data)

    return Response([])