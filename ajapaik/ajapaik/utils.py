from django.db.models import F
from django_comments import get_model
from allauth.socialaccount.models import SocialAccount

comment_model = get_model()


def get_comment_replies(comment):
    '''
    Returns queryset that contain all reply for given comment.
    '''
    return comment_model.objects.filter(
        parent_id=comment.pk
    ).exclude(parent_id=F('pk'))


def merge_profiles(profile, target_profile):
    from django.apps import apps
    from ajapaik.ajapaik.models import Album, AlbumPhoto, Dating, DatingConfirmation, DifficultyFeedback, GeoTag, ImageSimilarity, ImageSimilarityGuess, MyXtdComment, Photo, PhotoLike, Points, Skip, Transcription, TranscriptionFeedback
    from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, FaceRecognitionRectangleSubjectDataGuess, FaceRecognitionUserGuess
    from ajapaik.ajapaik_object_recognition.models import ObjectAnnotationFeedback, ObjectDetectionAnnotation
    profile_querysets = [
        ('ajapaik', Album.objects.filter(profile=target_profile)),
        ('ajapaik', AlbumPhoto.objects.filter(profile=target_profile)),
        ('ajapaik', Dating.objects.filter(profile=target_profile)),
        ('ajapaik', DatingConfirmation.objects.filter(profile=target_profile)),
        ('ajapaik', PhotoLike.objects.filter(profile=target_profile)),
    ]

    user_querysets = [
        ('ajapaik_face_recognition', FaceRecognitionRectangle.objects.filter(user=target_profile)),
        ('ajapaik_face_recognition', FaceRecognitionRectangleFeedback.objects.filter(user=target_profile)),
        ('ajapaik_face_recognition', FaceRecognitionUserGuess.objects.filter(user=target_profile)),
        ('ajapaik', GeoTag.objects.filter(user=target_profile)),
        ('ajapaik_object_recognition', ObjectAnnotationFeedback.objects.filter(user=target_profile)),
        ('ajapaik_object_recognition', ObjectDetectionAnnotation.objects.filter(user=target_profile)),
        ('ajapaik', Photo.objects.filter(user=target_profile)),
        ('ajapaik', Points.objects.filter(user=target_profile)),
        ('ajapaik', Skip.objects.filter(user=target_profile)),
        ('ajapaik', Transcription.objects.filter(user=target_profile)),
        ('ajapaik', TranscriptionFeedback.objects.filter(user=target_profile))
    ]

    user_profile_querysets = [
        ('ajapaik', DifficultyFeedback.objects.filter(user_profile=target_profile))
    ]

    user_last_modified_querysets = [
        ('ajapaik', ImageSimilarity.objects.filter(user_last_modified=target_profile))
    ]

    guesser_querysets = [
        ('ajapaik_face_recognition', FaceRecognitionRectangleSubjectDataGuess.objects.filter(guesser=target_profile)),
        ('ajapaik', ImageSimilarityGuess.objects.filter(guesser=target_profile))
    ]

    queryset_dictionary = {'profile': profile_querysets, 'user': user_querysets, 'user_profile': user_profile_querysets, 'user_last_modified': user_last_modified_querysets, 'guesser': guesser_querysets}

    for key, value in queryset_dictionary.items():
        for app_queryset_tuple in value:
            for item in app_queryset_tuple[1]:
                setattr(item, key, profile)
            Model = apps.get_model(app_queryset_tuple[0], app_queryset_tuple[1].model.__name__)
            Model.objects.bulk_update(app_queryset_tuple[1], [key])

    comments = MyXtdComment.objects.filter(user_id=target_profile.id)
    for comment in comments:
        comment.user=profile.user
    MyXtdComment.objects.bulk_update(comments, ['user'])

    attributes = dir(target_profile)
    attributes.remove('facebook')
    attributes.remove('objects')
    attributes.remove('__weakref__')
    attributes.remove('deletion_attempted')
    for attribute in attributes:
        attr = getattr(profile,attribute)
        attr2 = getattr(target_profile,attribute)
        if attr is None and attr2 is not None:
            setattr(profile, attribute, attr2)
    profile.save()

    socialAccounts = SocialAccount.objects.filter(user_id=target_profile.user.id)
    for socialAccount in socialAccounts:
        socialAccount.user = profile.user
        socialAccount.save()
    
    if not profile.user.is_superuser and target_profile.user.is_superuser:
        profile.user.is_superuser = target_profile.user.is_superuser
    if not profile.user.is_staff and target_profile.user.is_staff:
        profile.user.is_staff = target_profile.user.is_staff
    if not profile.user.is_active and target_profile.user.is_active:
        profile.user.is_active = target_profile.user.is_active
    profile.user.save()