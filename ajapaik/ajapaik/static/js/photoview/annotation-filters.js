'use strict';

function getCorrespondingAnnotations(annotationIdentifier) {
    var annotationsSelector = '[data-annotation-identifier="' + annotationIdentifier + '"]';
    return $(annotationsSelector);
}

function getClickEventCheckbox(event, checkboxId) {
    var hasClickedCheckBox = event.target.type === 'checkbox';

    if (hasClickedCheckBox) {
        return $(event.target);
    }

    return $('#' + checkboxId);
}

function getOnAnnotationCheckboxClick(annotationIdentifier, checkboxId) {
    return function(event) {
        var checkbox = getClickEventCheckbox(event, checkboxId);

        var isChecked = checkbox.is(':checked');
        var correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);

        correspondingAnnotations.css({visibility: isChecked ? '' : 'hidden'});
    };
}

function getDisplayCorrespondingFilter(annotationIdentifier) {
    return function() {
        var correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({display: 'initial'});
    };
}

function getHideCorrespondingFilter(annotationIdentifier) {
    return function() {
        var correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({display: 'none'});
    };
}

function getUnknownPersonTitle(annotationId) {
    var unknownPersonLabel = gettext('Unknown person');
    var annotationLabel = gettext('Annotation');

    return annotationLabel + ' ' + annotationId + ': ' + unknownPersonLabel;
}

function annotationCheckbox(annotation) {
    var checkboxName = !annotation.objectId
        ? 'face-annotation-' + annotation.id
        : 'object-annotation-' + annotation.id;

    var identifier = getAnnotationIdentifier(annotation);

    var labelText = annotation.label ? annotation.label : getUnknownPersonTitle(annotation.id);

    var wrapper = $('<div>');
    var eventWrapper = $('<span>', {
        mouseenter: getDisplayCorrespondingFilter(identifier),
        mouseleave: getHideCorrespondingFilter(identifier),
        click: getOnAnnotationCheckboxClick(identifier, checkboxName)
    });

    var label = $('<label>', {
        for: checkboxName
    });

    var input = $('<input>', {
        'data-corresponding-annotation-identifier': identifier,
        type: 'checkbox',
        id: checkboxName,
        name: checkboxName,
        style: 'margin-top:auto; margin-bottom: auto;',
        checked: true
    });

    return wrapper
        .append(eventWrapper
            .append(label
                .append(labelText)
            )
            .append(input)
        );
}

function createTitle(text) {
    var wrapper = $('<div>', {
        class: 'annotation-filters__title'
    });

    return wrapper.append(text);
}

function createAnnotationColumn() {
    return $('<div>', {
        class: 'col-md-6 annotation-filters__checkbox-column'
    });
}

function createRow(providedId) {
    var id = providedId ? providedId : '';

    return $('<div>', {
        class: 'row',
        id: id
    });
}

function createAnnotationColumns(annotations, titleKey) {
    var title = createTitle(gettext(titleKey));

    var divider = $('<hr/>');
    var wrapper = $('<div class="col-md-6"></div>');

    var columnOne = createAnnotationColumn();
    var columnTwo = createAnnotationColumn();

    annotations.forEach(function(object, index) {
        var objectCheckbox = annotationCheckbox(object);

        if (index % 2 === 0) {
            columnOne.append(objectCheckbox);
        } else {
            columnTwo.append(objectCheckbox);
        }
    });

    return wrapper
        .append(title)
        .append(divider)
        .append(createRow()
                .append(columnOne)
                .append(columnTwo)
        );
}

function createAnnotationFiltersContent(allAnnotationLabels) {
    var objectColumn = createAnnotationColumns(allAnnotationLabels.objects, 'Objects');
    var faceColumn = createAnnotationColumns(allAnnotationLabels.faces, 'Faces');

    return createRow(constants.elements.ANNOTATION_FILTERS_ID)
        .append(objectColumn)
        .append(faceColumn);
}

function collectAllLabels(detections) {
    var objects = [];
    var addedObjects = [];

    var faces = [];
    var addedSubjects = [];

    detections.forEach(function(detection) {
        var isUnknownPersonDetection = !detection.subjectId && !detection.objectId;
        var isUniqueObjectDetection = detection.objectId && addedObjects.indexOf(detection.objectId) === -1;
        var isUniqueSubjectDetection = !detection.objectId && addedSubjects.indexOf(detection.subjectId) === -1;

        if (isUniqueObjectDetection) {
            addedObjects.push(detection.objectId);
            objects.push({
                id: detection.id,
                objectId: detection.objectId,
                label: detection.objectLabel
            });
        } else if (isUnknownPersonDetection || isUniqueSubjectDetection) {
            if (detection.subjectId) {
                addedSubjects.push(detection.subjectId);
            }

            faces.push({
                id: detection.id,
                subjectId: detection.subjectId,
                label: detection.subjectName
            });
        }
    });

    return {
        objects: objects,
        faces: faces
    };
}

function createAnnotationFilters(detections) {
    var FILTERS_ALREADY_EXIST = false;
    var NEW_FILTERS_HAVE_BEEN_DRAWN = true;

    var hasAlreadyDrawnFilters = $('#' + constants.elements.ANNOTATION_FILTERS_ID).length !== 0;

    if (hasAlreadyDrawnFilters) {
        return FILTERS_ALREADY_EXIST;
    }

    var allLabels = collectAllLabels(detections);

    var filtersWrapper = $('#annotation-filters-wrapper');

    filtersWrapper.append(createAnnotationFiltersContent(allLabels));

    return NEW_FILTERS_HAVE_BEEN_DRAWN;
}
