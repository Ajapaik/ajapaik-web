'use strict';

function getObjectAnnotationClasses() {
    var objectClasses = getDataWithExpirationValidation(cacheKeys.objectClasses);

    if (objectClasses) {
        return;
    }

    var onSuccess = function(response) {
        storeData(cacheKeys.objectClasses, response.data);
    };

    getRequest(
      '/object-recognition/get-object-annotation-classes',
        null,
        null,
        constants.translations.queries.GET_ANNOTATION_CLASSES_FAILED,
        onSuccess
    );
}

function getAllAnnotations(customOnSuccess) {
    var photoId = ObjectTagger.getPhotoId();

    var onSuccess = function(response) {
        var result = response.data.map(function(rectangle) {
            return JSON.parse(rectangle);
        });

        window.annotations = result;

        if (customOnSuccess) {
            customOnSuccess(result);
        }
    };

    getRequest(
      '/object-recognition/get-all-face-and-object-annotations/' + photoId + '/',
        null,
        null,
        constants.translations.queries.GET_ANNOTATIONS_FAILED,
        onSuccess
    );
}

function addNewDetectionAnnotation(payload, onSuccess) {
    payload.csrfmiddlewaretoken = window.docCookies.getItem('csrftoken');

    var successMessage = constants.translations.queries.ADD_FACE_ANNOTATION_SUCCESS;
    var failMessage = constants.translations.queries.ADD_FACE_ANNOTATION_FAILED;

    if(payload.isSavingObject) {
        successMessage = constants.translations.queries.ADD_OBJECT_ANNOTATION_SUCCESS;
        failMessage = constants.translations.queries.ADD_OBJECT_ANNOTATION_FAILED;
    }

    postRequest(
        '/object-recognition/add-annotation',
        payload,
        successMessage,
        failMessage,
        onSuccess
    );
}

function updateExistingObjectDetectionAnnotation(payload, onSuccess) {
    payload.csrfmiddlewaretoken = window.docCookies.getItem('csrftoken');

    putRequest(
        '/object-recognition/update-annotation',
        payload,
        constants.translations.queries.UPDATE_OBJECT_ANNOTATION_SUCCESS,
        constants.translations.queries.UPDATE_OBJECT_ANNOTATION_FAILED,
        onSuccess
    );
}

function deleteSavedObjectAnnotation(annotationId, onSuccess) {
    deleteRequest(
        '/object-recognition/remove-annotation/' + annotationId,
        constants.translations.queries.REMOVE_OBJECT_ANNOTATION_SUCCESS,
        constants.translations.queries.REMOVE_OBJECT_ANNOTATION_FAILED,
        onSuccess
    );
}

function addObjectAnnotationFeedback(annotationId, payload, onSuccess) {
    payload.csrfmiddlewaretoken = window.docCookies.getItem('csrftoken');

    postRequest(
        '/object-recognition/annotation/' + annotationId + '/feedback/',
        payload,
        constants.translations.queries.ADD_OBJECT_ANNOTATION_FEEDBACK_SUCCESS,
        constants.translations.queries.ADD_OBJECT_ANNOTATION_FEEDBACK_FAILED,
        onSuccess
    );
}

function addFaceAnnotationFeedback(annotationId, payload, onSuccess) {
    payload.csrfmiddlewaretoken = window.docCookies.getItem('csrftoken');

    postRequest(
        '/face-recognition/annotation/' + annotationId + '/feedback/',
        payload,
        constants.translations.queries.UPDATE_OBJECT_ANNOTATION_SUCCESS,
        constants.translations.queries.UPDATE_OBJECT_ANNOTATION_FAILED,
        onSuccess
    );
}

function editFaceAnnotation(payload, onSuccess) {
    payload.csrfmiddlewaretoken = window.docCookies.getItem('csrftoken');

    postRequest(
        '/face-recognition/api/v1/subject-data/',
        payload,
        constants.translations.queries.UPDATE_FACE_ANNOTATION_SUCCESS,
        constants.translations.queries.UPDATE_FACE_ANNOTATION_FAILED,
        onSuccess
    );
}

function removeFaceAnnotation(annotationId, onSuccess) {
    deleteRequest(
        '/face-recognition/remove-annotation/' + annotationId + '/',
        constants.translations.queries.REMOVE_FACE_ANNOTATION_SUCCESS,
        constants.translations.queries.REMOVE_FACE_ANNOTATION_FAILED,
        onSuccess
    );
}
