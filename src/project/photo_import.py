from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from models import Photo, City
from project.serializers import PhotoSerializer, CitySerializer

class PhotoViewSet(viewsets.ModelViewSet):
	queryset = Photo.objects.all()
	serializer_class = PhotoSerializer
	permission_classes = (IsAdminUser,)

	def get_queryset(self):
		queryset = Photo.objects.all()
		source_keys = self.request.QUERY_PARAMS.getlist('source_keys', None)
		if source_keys is not None:
			queryset = queryset.filter(source_key__in=source_keys)
		return queryset

class CityViewSet(viewsets.ModelViewSet):
	queryset = City.objects.all()
	serializer_class = CitySerializer
	permission_classes = (IsAdminUser,)