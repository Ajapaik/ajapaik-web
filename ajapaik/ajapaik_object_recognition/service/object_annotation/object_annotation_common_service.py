from ajapaik.ajapaik_curator.curator_drivers import wikidata
from ajapaik.ajapaik_object_recognition.models import ObjectAnnotationClass, ObjectDetectionModel
from ajapaik.ajapaik_object_recognition.service.object_annotation import detection_models


def get_saved_label(label_wikidata_id):
    saved_label = __get_saved_label(label_wikidata_id)

    if saved_label is None:
        new_annotation_class = ObjectAnnotationClass()

        new_annotation_class.wikidata_id = label_wikidata_id
        new_annotation_class.translations = wikidata.get_label_translation(label_wikidata_id)
        new_annotation_class.detection_model = ObjectDetectionModel.objects \
            .get(model_file_name=detection_models.OBJECT_DETECTION_MODEL_NAME)

        new_annotation_class.save()

        return new_annotation_class

    return saved_label


def __get_saved_label(label_wikidata_id):
    try:
        saved_label = ObjectAnnotationClass.objects.get(wikidata_id=label_wikidata_id)

        translations = wikidata.get_label_translation(label_wikidata_id)
        saved_label.translations = translations
        saved_label.save()

        return saved_label
    except ObjectAnnotationClass.DoesNotExist:
        return None
