from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, BasePermission
from rest_framework.response import Response
from models import Photo, Area, Source, Album
from project.home.serializers import PhotoSerializer, AreaSerializer, SourceSerializer, AlbumSerializer
from rest_framework import status


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'POST']:
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

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = (IsAdminUser, CustomPermission)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
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