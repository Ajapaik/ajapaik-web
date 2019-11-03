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

        correspondingAnnotations.css({display: isChecked ? 'initial' : 'none'});
    };
}

function getDisplayCorrespondingFilter(annotationIdentifier) {
    return function() {
        var correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({visibility: ''});
    };
}

function getHideCorrespondingFilter(annotationIdentifier) {
    return function() {
        var correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({visibility: 'hidden'});
    };
}

function getUnknownPersonTitle(annotationId) {
    var unknownPersonLabel = gettext('Unknown');

    return unknownPersonLabel + ' (id: ' + annotationId + ')';
}

function createAnnotationFilteringCheckbox(checkboxName, annotationIdentifier, labelText) {
    var wrapper = $('<div class="form-check">');

    var input = $('<input>', {
        class: 'form-check-input',
        type: 'checkbox',
        id: checkboxName,
        name: checkboxName,
        checked: true
    });

    var label = $('<label>', {
        class: 'form-check-label',
        for: checkboxName
    });

    label.append(labelText);

    var eventWrapper = $('<span>', {
        mouseenter: getDisplayCorrespondingFilter(annotationIdentifier),
        mouseleave: getHideCorrespondingFilter(annotationIdentifier),
        click: getOnAnnotationCheckboxClick(annotationIdentifier, checkboxName)
    });

    return wrapper
        .append(eventWrapper
            .append(input)
            .append(label)
        );
}

function annotationCheckbox(annotation) {
    var checkboxName = !annotation.wikiDataId
        ? 'face-annotation-' + annotation.id
        : 'object-annotation-' + annotation.id;

    var identifier = getAnnotationIdentifier(annotation);

    var labelText = annotation.label ? annotation.label : getUnknownPersonTitle(annotation.id);

    return createAnnotationFilteringCheckbox(checkboxName, identifier, labelText);
}

function createTitle(text) {
    var wrapper = $('<div>', {
        class: 'annotation-filters__title'
    });

    return wrapper.append(text);
}

function createAnnotationColumn() {
    return $('<div>', {
        class: 'col-md-12 annotation-filters__checkbox-column'
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
        var isUnknownPersonDetection = !detection.subjectId && !detection.wikiDataId;
        var isUniqueObjectDetection = detection.wikiDataId && addedObjects.indexOf(detection.wikiDataId) === -1;
        var isUniqueSubjectDetection = !detection.wikiDataId && addedSubjects.indexOf(detection.subjectId) === -1;

        if (isUniqueObjectDetection) {
            addedObjects.push(detection.wikiDataId);
            objects.push({
                id: detection.id,
                wikiDataId: detection.wikiDataId,
                label: getLanguageSpecificTranslation(detection.translations)
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
    var NEW_FILTERS_HAVE_BEEN_DRAWN = true;
    var filtersWrapper = $('#annotation-filters-wrapper');

    filtersWrapper.empty();

    var allLabels = collectAllLabels(detections);

    filtersWrapper.append(createAnnotationFiltersContent(allLabels));

    return NEW_FILTERS_HAVE_BEEN_DRAWN;
}
