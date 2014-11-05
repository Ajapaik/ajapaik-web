from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, BasePermission
from rest_framework.response import Response
from models import Photo, City, Source
from project.serializers import PhotoSerializer, CitySerializer, SourceSerializer
from rest_framework import status

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

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.DATA, files=request.FILES)

		existing_photo_with_source_key = Photo.objects.filter(source_key=serializer.source_key)

		if serializer.is_valid() and not existing_photo_with_source_key:
			self.pre_save(serializer.object)
			self.object = serializer.save(force_insert=True)
			self.post_save(self.object, created=True)
			headers = self.get_success_headers(serializer.data)
			return Response(serializer.data, status=status.HTTP_201_CREATED,
							headers=headers)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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