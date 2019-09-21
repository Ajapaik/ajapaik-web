from ajapaik.ajapaik.models import Profile
from ajapaik.ajapaik_object_recognition.domain.add_object_detection_feedback import AddObjectDetectionFeedback
from ajapaik.ajapaik_object_recognition.domain.remove_object_annotation_feedback import RemoveObjectAnnotationFeedback
from ajapaik.ajapaik_object_recognition.models import ObjectAnnotationFeedback, ObjectDetectionAnnotation
from ajapaik.ajapaik_object_recognition.service.object_annotation import object_annotation_common_service


def set_feedback(
        feedback: ObjectAnnotationFeedback,
        request: AddObjectDetectionFeedback,
        user: Profile,
        annotation: ObjectDetectionAnnotation
):
    feedback.confirmation = request.is_confirmation
    feedback.user = user
    feedback.object_detection_annotation = annotation

    if request.alternative_wiki_data_label_id is not None and len(request.alternative_wiki_data_label_id) > 0:
        alternative_object_suggestion = object_annotation_common_service\
            .get_saved_label(request.alternative_wiki_data_label_id)
        feedback.alternative_object = alternative_object_suggestion
    else:
        feedback.alternative_object = None


def add_feedback(request: AddObjectDetectionFeedback):
    annotation_id = request.object_annotation_id

    annotation = ObjectDetectionAnnotation.objects.get(pk=annotation_id)
    user = Profile.objects.get(pk=request.user_id)

    existing_feedback = get_existing_feedback(annotation, user)

    if existing_feedback is not None:
        set_feedback(existing_feedback, request, user, annotation)
        existing_feedback.save()
    else:
        new_feedback = ObjectAnnotationFeedback()
        set_feedback(new_feedback, request, user, annotation)
        new_feedback.save()


def get_existing_feedback(annotation: ObjectDetectionAnnotation, user: Profile):
    try:
        return ObjectAnnotationFeedback.objects.get(
            user_id=user.id,
            object_detection_annotation_id=annotation.id
        )
    except ObjectAnnotationFeedback.DoesNotExist:
        return None


def remove_feedback(remove_object_annotation_feedback: RemoveObjectAnnotationFeedback):
    user_id = remove_object_annotation_feedback.user_id
    annotation_id = remove_object_annotation_feedback.annotation_id

    user = Profile.objects.get(pk=user_id)
    object_annotation = ObjectDetectionAnnotation.objects.get(pk=annotation_id)

    existing_feedback = ObjectAnnotationFeedback.objects.get(user=user, object_detection_annotation=object_annotation)

    existing_feedback.delete()
