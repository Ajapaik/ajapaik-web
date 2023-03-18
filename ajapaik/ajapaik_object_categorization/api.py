from django.http import JsonResponse

from ajapaik.ajapaik.api import AjapaikAPIView, PLEASE_LOGIN

from django.shortcuts import get_object_or_404

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class Category(AjapaikAPIView):
    '''
    API Endpoint to get annotation data
    '''

    @staticmethod
    def get(request, photo_id):
        # try:
        #     if request.user.is_anonymous:
        #         return JsonResponse({'error': PLEASE_LOGIN}, status=401)
        #
        #     photo = get_object_or_404(Photo, id=photo_id)
        #     scene = 'undefined'
        #     scene_consensus = 'undefined'
        #     viewpoint_elevation = 'undefined'
        #     viewpoint_elevation_consensus = 'undefined'
        #     viewpoint_elevation_suggestion = PhotoViewpointElevationSuggestion.objects \
        #         .filter(photo=photo, proposer=request.user.profile).order_by('-created').first()
        #     if viewpoint_elevation_suggestion:
        #         if viewpoint_elevation_suggestion.viewpoint_elevation == 0:
        #             viewpoint_elevation = 'Ground'
        #         if viewpoint_elevation_suggestion.viewpoint_elevation == 1:
        #             viewpoint_elevation = 'Raised'
        #         if viewpoint_elevation_suggestion.viewpoint_elevation == 2:
        #             viewpoint_elevation = 'Aerial'
        #
        #     scene_suggestion = PhotoSceneSuggestion.objects.filter(photo=photo, proposer=request.user.profile).order_by(
        #         '-created').first()
        #
        #     if scene_suggestion:
        #         if scene_suggestion.scene == 0:
        #             scene = 'Interior'
        #         if scene_suggestion.scene == 1:
        #             scene = 'Exterior'
        #
        #     if photo.scene == 0:
        #         scene_consensus = 'Interior'
        #     if photo.scene == 1:
        #         scene_consensus = 'Exterior'
        #
        #     if photo.viewpoint_elevation == 0:
        #         viewpoint_elevation_consensus = 'Ground'
        #     if photo.viewpoint_elevation == 1:
        #         viewpoint_elevation_consensus = 'Raised'
        #     if photo.viewpoint_elevation == 2:
        #         viewpoint_elevation_consensus = 'Aerial'

            return JsonResponse(
                {'scene': 1, 'scene_consensus': 1, 'viewpoint_elevation': 1,
                 'viewpoint_elevation_consensus': 1})
        # except:  # noqa
        #     return JsonResponse({'error': _('Something went wrong')}, status=500)
