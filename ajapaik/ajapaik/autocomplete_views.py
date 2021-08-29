from dal import autocomplete
from django.db.models import Q
from django.http.response import HttpResponse
from django.utils.translation import gettext as _
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from ajapaik.ajapaik.models import Album, AlbumPhoto, Area, Dating, DatingConfirmation, Device, \
    GeoTag, GoogleMapsReverseGeocode, ImageSimilarity, ImageSimilaritySuggestion, Licence, \
    Location, Photo, Points, Profile, Skip, Source, Transcription, User, Video
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionUserSuggestion, FaceRecognitionRectangleSubjectDataSuggestion
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass, \
    ObjectAnnotationFeedback


class AlbumAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Album.objects.none()

        qs = Album.objects.all()

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(name_et__icontains=self.q) | Q(name_en__icontains=self.q) | Q(
                name_ru__icontains=self.q) | Q(name_fi__icontains=self.q) | Q(name_sv__icontains=self.q) | Q(
                name_nl__icontains=self.q) | Q(name_de__icontains=self.q) | Q(name_no__icontains=self.q) | Q(
                name_lv__icontains=self.q) | Q(name_lt__icontains=self.q))

        return qs


class AlbumPhotoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AlbumPhoto.objects.none()

        qs = AlbumPhoto.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class AreaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Area.objects.none()

        qs = Area.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class DatingAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Dating.objects.none()

        qs = Dating.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class DatingConfirmationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DatingConfirmation.objects.none()

        qs = DatingConfirmation.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class DeviceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Device.objects.none()

        qs = Device.objects.all()

        if self.q:
            qs = qs.filter(camera_model__istartswith=self.q)

        return qs


class FaceRecognitionRectangleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return FaceRecognitionRectangle.objects.none()

        qs = FaceRecognitionRectangle.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class FaceRecognitionRectangleFeedbackAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return FaceRecognitionRectangleFeedback.objects.none()

        qs = FaceRecognitionRectangleFeedback.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class FaceRecognitionUserSuggestionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return FaceRecognitionUserSuggestion.objects.none()

        qs = FaceRecognitionUserSuggestion.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class FaceRecognitionRectangleSubjectDataSuggestionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return FaceRecognitionRectangleSubjectDataSuggestion.objects.none()

        qs = FaceRecognitionRectangleSubjectDataSuggestion.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class GeoTagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return GeoTag.objects.none()

        qs = GeoTag.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs

class GoogleMapsReverseGeocodeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return GoogleMapsReverseGeocode.objects.none()
        qs = GoogleMapsReverseGeocode.objects.all()
        if self.q:
            qs = qs.filter(response__icontains=self.q)
        
        return qs


class ImageSimilarityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ImageSimilarity.objects.none()

        qs = ImageSimilarity.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class ImageSimilaritySuggestionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ImageSimilaritySuggestion.objects.none()

        qs = ImageSimilaritySuggestion.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class LicenceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Licence.objects.none()

        qs = Licence.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Location.objects.none()

        qs = Location.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class ObjectDetectionAnnotationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ObjectDetectionAnnotation.objects.none()

        qs = ObjectDetectionAnnotation.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class ObjectAnnotationClassAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ObjectAnnotationClass.objects.none()

        qs = ObjectAnnotationClass.objects.all()

        if self.q:
            qs = qs.filter(alias__istartswith=self.q)

        return qs


class ObjectAnnotationFeedbackAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ObjectAnnotationFeedback.objects.none()

        qs = ObjectAnnotationFeedback.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class PhotoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Photo.objects.none()

        qs = Photo.objects.all()

        if self.q:
            qs = qs.filter(Q(id__istartswith=self.q) | Q(description__istartswith=self.q))

        return qs


class PointsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Points.objects.none()

        qs = Points.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Profile.objects.none()

        qs = Profile.objects.all()

        if self.q:
            qs = qs.filter(
                Q(last_name__icontains=self.q) | Q(first_name__icontains=self.q) | Q(fb_name__icontains=self.q) | Q(
                    google_plus_name__icontains=self.q))

        return qs


class OpenAlbumAutocomplete(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Album.objects.none()

        q = request.GET.get('q')
        exclude = request.GET.getlist('exclude')

        qs = Album.objects.all().exclude(id__in=exclude)

        if q:
            qs = qs.filter(Q(profile=request.user.profile) | Q(open=True)).filter(
                Q(name__icontains=q) | Q(name_et__icontains=q) | Q(name_en__icontains=q) | Q(name_ru__icontains=q) | Q(
                    name_fi__icontains=q) | Q(name_sv__icontains=q) | Q(name_nl__icontains=q) | Q(
                    name_de__icontains=q) | Q(name_no__icontains=q) | Q(name_lv__icontains=q) | Q(name_lt__icontains=q))

        result = """<span class="block"><em>""" + _("No album found") + """</em></span>"""
        if len(qs) > 0:
            result = ''
            for q in qs:
                result += '<span data-value=' + str(q.id) + '>' + q.name + '</span>'
        return HttpResponse(result, status=200)


class SkipAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Skip.objects.none()

        qs = Skip.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class SourceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Source.objects.none()

        qs = Source.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class SubjectAlbumAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Album.objects.none()

        qs = Album.objects.filter(atype=Album.PERSON)

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(name_et__icontains=self.q) | Q(name_en__icontains=self.q) | Q(
                name_ru__icontains=self.q) | Q(name_fi__icontains=self.q) | Q(name_sv__icontains=self.q) | Q(
                name_nl__icontains=self.q) | Q(name_de__icontains=self.q) | Q(name_no__icontains=self.q) | Q(
                name_lv__icontains=self.q) | Q(name_lt__icontains=self.q))
        for q in qs:
            if q.gender is not None and q.gender > -1:
                q.name = q.name + ';' + str(q.gender)
            else:
                q.name = q.name + ';-1'

        return qs


class TranscriptionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Transcription.objects.none()

        qs = Transcription.objects.all()

        if self.q:
            qs = qs.filter(id__istartswith=self.q)

        return qs


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(username__icontains=self.q)

        return qs


class VideoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Video.objects.none()

        qs = Video.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
