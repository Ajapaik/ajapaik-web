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

function getUnknownAnnotationTitle(annotationId) {
    var unknownPersonLabel = gettext('Unknown');

    return unknownPersonLabel + ' (id: ' + annotationId + ')';
}

function createAnnotationFilteringCheckbox(checkboxName, annotationIdentifier, labelText) {
    var wrapper = $('<div class="form-check" style="padding-top: 4px;">');

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

function isFaceAnnotation(annotation) {
    return !annotation.wikiDataId;
}

function annotationCheckbox(annotation) {
    var checkboxName = isFaceAnnotation(annotation)
        ? 'face-annotation-' + annotation.id
        : 'object-annotation-' + annotation.id;

    var identifier = getAnnotationIdentifier(annotation);

    var labelText = annotation.label ? annotation.label : getUnknownAnnotationTitle(annotation.id);

    return createAnnotationFilteringCheckbox(checkboxName, identifier, labelText);
}

function createAnnotationColumn(columnSize) {
    return $('<div>', {
        class: 'col-md-' + columnSize + ' annotation-filters__checkbox-column'
    });
}

function createRow(providedId) {
    var id = providedId ? providedId : '';

    return $('<div>', {
        class: 'row',
        id: id
    });
}

function createAnnotationColumns(annotations) {
    var numberOfColumns = parseInt($('#filter-number-of-columns').text());
    var columns = createNumberOfColumns(numberOfColumns);

    annotations.forEach(function(annotation, index) {
        var toggleAnnotationCheckbox = annotationCheckbox(annotation);
        addAnnotationToColumn(columns, annotation, index, toggleAnnotationCheckbox);
    });

    return createRow()
        .append(columns);
}

function addAnnotationToColumn(columns, annotation, index, annotationCheckbox) {
    for (var i = columns.length; i > 0; i--) {
        if (index % i === 0) {
            return columns[index % columns.length].append(annotationCheckbox);
        }
    }
}

function createNumberOfColumns(numberOfColumns) {
    var columns = [];
    var columnSize = 12 / numberOfColumns;

    for (var i = 0; i < numberOfColumns; i++) {
        columns.push(createAnnotationColumn(columnSize));
    }

    return columns;
}

function createFaceAnnotationFiltersContent(faceAnnotations) {
    return $('#' + constants.elements.FACE_ANNOTATION_FILTERS_ID)
        .append(createAnnotationColumns(faceAnnotations));
}

function createObjectAnnotationFiltersContent(objectAnnotations) {
    return $('#' + constants.elements.OBJECT_ANNOTATION_FILTERS_ID)
        .append(createAnnotationColumns(objectAnnotations));
}

function isOptionalUnsureValuePresent(value) {
    return !!value && value.toUpperCase() !== 'UNSURE';
}

function getGenderAndAgeForLabel(annotation) {
    return [annotation.gender, annotation.age]
        .filter(function(extraInfo) {
            return isOptionalUnsureValuePresent(extraInfo);
        })
        .map(function(extraInfo) {
            return gettext(capitalizeFirstLetter(extraInfo));
        })
        .join(', ');
}

function getSubjectCheckboxLabel(annotation) {
    var label = '';

    if (annotation.subjectName) {
        label += (annotation.subjectName + ' ');

        if (isOptionalUnsureValuePresent(annotation.gender) || isOptionalUnsureValuePresent(annotation.age)) {
            label += '- ';
        }
    }

    if (annotation.gender || annotation.age) {
        label += getGenderAndAgeForLabel(annotation);
    }

    if (label && !annotation.subjectName) {
        label += ' (id: ' + annotation.id + ')';
    }

    return label;
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
                label: getSubjectCheckboxLabel(detection)
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
    var personFiltersWrapper = $('#person-annotation-filters');
    var objectFiltersWrapper = $('#object-annotation-filters');

    personFiltersWrapper.empty();
    objectFiltersWrapper.empty();

    var allLabels = collectAllLabels(detections);

    personFiltersWrapper.append(createFaceAnnotationFiltersContent(allLabels.faces));
    objectFiltersWrapper.append(createObjectAnnotationFiltersContent(allLabels.objects));

    return NEW_FILTERS_HAVE_BEEN_DRAWN;
}
