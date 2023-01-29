from ajapaik.ajapaik.curator_drivers import wikidata
from ajapaik.ajapaik_object_recognition.models import ObjectAnnotationClass, ObjectDetectionModel
from ajapaik.ajapaik_object_recognition.service.object_annotation import detection_models


def get_saved_label(label_wiki_data_id):
    saved_label = __get_saved_label(label_wiki_data_id)
    if saved_label:
        return saved_label

    return ObjectAnnotationClass.objects.create(
        wiki_data_id=label_wiki_data_id,
        translations=wikidata.get_label_translation(label_wiki_data_id),
        detection_model=ObjectDetectionModel.objects.get(
            model_file_name=detection_models.OBJECT_DETECTION_MODEL_NAME)
    )


def __get_saved_label(label_wiki_data_id):
    try:
        saved_label = ObjectAnnotationClass.objects.get(wiki_data_id=label_wiki_data_id)

        translations = wikidata.get_label_translation(label_wiki_data_id)
        saved_label.translations = translations
        saved_label.save(update_fields=['translations'])

        return saved_label
    except ObjectAnnotationClass.DoesNotExist:
        return None
