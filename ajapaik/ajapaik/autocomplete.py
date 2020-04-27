from django.forms import ModelForm
from dal import autocomplete

from ajapaik.ajapaik.models import Album, AlbumPhoto, Area, Dating, DatingConfirmation, Device, GeoTag, ImageSimilarity, ImageSimilarityGuess, Licence, Photo, Points, Profile, Skip, Source, User, Video
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, FaceRecognitionUserGuess, FaceRecognitionRectangleSubjectDataGuess
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass, ObjectAnnotationFeedback

def autocomplete_form_factory(ac_model, custom_url=None, *args, **kwargs):
    field_url_dict = {}
    m2m = ('photos', 'videos', 'similar_photos')
    if ac_model == Album:
        field_url_dict = {
            'subalbum_of': 'album',
            'profile': 'profile',
            'photos': 'photo',
            'videos': 'video',
            'cover_photo': 'photo',
            'source': 'source'
        }
    elif ac_model == AlbumPhoto:
        field_url_dict = {
            'album': 'album',
            'photo': 'photo',
            'profile': 'profile'
        }
    elif ac_model ==  DatingConfirmation:
        field_url_dict = {
            'confirmation_of': 'dating',
            'profile': 'profile'
        }
    elif ac_model ==  FaceRecognitionRectangle:
        field_url_dict = {
            'photo': 'photo',
            'subject_consensus': 'album',
            'subject_ai_guess': 'album',
            'user': 'profile'
        }
    elif ac_model ==  FaceRecognitionRectangleFeedback:
        field_url_dict = {
            'rectangle': 'face-recognition-rectangle',
            'user': 'profile',
            'alternative_subject': 'album'
        }
    elif ac_model ==  FaceRecognitionUserGuess:
        field_url_dict = {
            'subject_album': 'album',
            'rectangle': 'face-recognition-rectangle',
            'user': 'user'
        }
    elif ac_model == FaceRecognitionRectangleSubjectDataGuess:
        field_url_dict = {
            'face_recognition_rectangle': 'face-recognition-rectangle',
            'guesser': 'profile'
        }
    elif ac_model ==  GeoTag:
        field_url_dict = {
            'user': 'profile',
            'photo': 'photo'
        }
    elif ac_model == ImageSimilarity:
        field_url_dict = {
            'from_photo': 'photo',
            'to_photo': 'photo',
            'user_last_modified': 'profile'
        }
    elif ac_model == ImageSimilarityGuess:
        field_url_dict = {
            'image_similarity': 'image-similarity',
            'guesser': 'profile'
        }
    elif ac_model == ObjectDetectionAnnotation:
        field_url_dict = {
            'photo': 'image_similarity',
            'detected_object': 'object-annotation-class',
            'user': 'profile',
        }
    elif ac_model == ObjectAnnotationClass:
        field_url_dict = {
            'detection_model': 'object-detection-model'
        }
    elif ac_model == ObjectAnnotationFeedback:
        field_url_dict = {
            'object_detection_annotation': 'object-detection-annotation',
            'alternative_object': 'object-annotation-class',
            'user': 'profile'
        }
    elif ac_model ==  Photo:
        field_url_dict = {
            'similar_photos': 'image-similarity',
            'licence': 'licence',
            'user': 'profile',
            'source': 'source',
            'device': 'device',
            'area': 'area',
            'rephoto_of': 'photo',
            'video': 'video',
            'postcard_back_of': 'photo',
            'postcard_front_of': 'photo'
        }
    elif ac_model ==  Points:
        field_url_dict = {
            'user': 'profile',
            'photo': 'photo',
            'album': 'album',
            'geotag': 'geotag',
            'dating': 'dating',
            'dating_confirmation': 'dating-confirmation',
            'annotation': 'face-recognition-rectangle',
            'face_recognition_rectangle_subject_data_guess': 'face-recognition-rectangle-subject-data-guess',
            'subject_confirmation': 'face-recognition-user-guess',
            'image_similarity_confirmation': 'image-similarity-guess',
            'transcription': 'transcription'
        }    
    elif ac_model ==  Skip:
        field_url_dict = {
            'user':'profile',
            'photo':'photo'
        }    
    elif ac_model ==  Video:
        field_url_dict = {
            'source': 'source'
        }
    else:
        field_url_dict = {}  

    # Assign the appropriate widgets based on this model's autocomplete dictionary
    ac_widgets = {}
    ac_fields = kwargs.get('fields', ('__all__'))
    for field, url in field_url_dict.items():
        is_m2m = field in m2m
        text = 'Type to return a list of %s...' if is_m2m else 'Type to return a %s list...'
        if ac_model in [AlbumPhoto, Dating, DatingConfirmation, FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, FaceRecognitionUserGuess, FaceRecognitionRectangleSubjectDataGuess, GeoTag, ImageSimilarity, ImageSimilarityGuess, ObjectDetectionAnnotation, ObjectAnnotationFeedback, Points,  Skip]:
            minimum_input_length = 1
        else:
            minimum_input_length = 3
        if custom_url is not None:
            url = custom_url
        kwargs = {
            'url': '%s-autocomplete' % url,
            'attrs': {
                'data-placeholder': text % ac_model._meta.get_field(field).verbose_name,
                'data-minimum-input-length': minimum_input_length,
            }
        }
        ac_widgets[field] = autocomplete.ModelSelect2Multiple(**kwargs) if is_m2m else autocomplete.ModelSelect2(**kwargs)

    # Create the form
    class DynamicAutocompleteForm(ModelForm):
        class Meta:
            model = ac_model
            fields = ac_fields
            widgets = ac_widgets

    return DynamicAutocompleteForm