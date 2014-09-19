from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, BasePermission
from models import Photo, City, Source
from project.serializers import PhotoSerializer, CitySerializer, SourceSerializer

class CustomPermission(BasePermission):
	def has_permission(self, request, view):
		if request.method in ['GET','POST']:
			return True
		return False

class PhotoViewSet(viewsets.ModelViewSet):
	queryset = Photo.objects.all()
	serializer_class = PhotoSerializer
	permission_classes = (IsAdminUser, CustomPermission)

	def get_queryset(self):
		queryset = Photo.objects.all()
		source_keys = self.request.QUERY_PARAMS.getlist('source_keys')
		if len(source_keys) > 0:
			queryset = queryset.filter(source_key__in=source_keys)
		return queryset

class CityViewSet(viewsets.ModelViewSet):
	queryset = City.objects.all()
	serializer_class = CitySerializer
	permission_classes = (IsAdminUser, CustomPermission)

class SourceViewSet(viewsets.ModelViewSet):
	queryset = Source.objects.all()
	serializer_class = SourceSerializer
	permission_classes = (IsAdminUser, CustomPermission)

	def get_queryset(self):
		queryset = Source.objects.all()
		source_descriptions = self.request.QUERY_PARAMS.getlist('source_descriptions')
		if len(source_descriptions) > 0:
			queryset = queryset.filter(description__in=source_descriptions)
		return queryset