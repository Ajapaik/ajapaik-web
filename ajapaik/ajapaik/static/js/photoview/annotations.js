'use strict';

function getCorrespondingAnnotations(annotationIdentifier) {
    let annotationsSelector = '[data-annotation-identifier="' + annotationIdentifier + '"]';
    return $(annotationsSelector);
}

function openAnnotationRectanglePopover(id) {
    if (!$('#modify-detected-object-annotation').is(":visible")) {
        setTimeout(() => { $('#ajp-face-modify-rectangle-' + id).click(); }, 10);
        $('#ajp-face-modify-rectangle-' + id).css('visibility', 'visible');
    }
}

function getDisplayCorrespondingAnnotation(annotationIdentifier) {
    if (!window.isAnnotatingDisabled) {
        hideAnnotationsWithoutOpenPopover();
        let correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({visibility: ''});
    }
}

function getHideCorrespondingAnnotation(annotationIdentifier) {
    if (!window.openPersonPopoverLabelIds || !window.openPersonPopoverLabelIds.includes(annotationIdentifier)) {
        let correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({visibility: 'hidden'});
    }
}

function toggleAnnotationLabelPopover(event, annotation, faceAnnotations) {
    event.preventDefault();
    if (!window.isAnnotatingDisabled) {
        let popoverTarget = $(event.target).data("bs.popover") === undefined
            ? $(event.target).parents('[data-toggle="popover"]')
            : $(event.target);
        
        if (popoverTarget.attr('aria-describedby') == undefined) {
            $('.ajp-person-label-popover').not('[id=' + popoverTarget.attr('aria-describedby') +']').popover('hide');
            popoverTarget.popover('show');
            $('[id=' + popoverTarget.attr('aria-describedby') + ']').addClass('ajp-person-label-popover');
            if (annotation.isAlbum) {
                displayAnnotations(true);
                window.openPersonPopoverLabelIds = faceAnnotations.filter(fa=>fa!==null).map(fa=>getAnnotationIdentifier(fa));
            } else {
                window.openPersonPopoverLabelIds = [getAnnotationIdentifier(annotation)];
                $('#ajp-face-modify-rectangle-' + annotation.id).css('visibility', 'visible');
            }
        } else {
            $('.ajp-person-label-popover').popover('hide');
            window.openPersonPopoverLabelIds = [];
            hideAnnotationsWithoutOpenPopover();
        }
    }
}

function createTaggingButton(title, iconText, spanText, action) {
    let button = $('<button>', {
        title,
        class: 'btn btn-light d-flex align-items-center w-100 my-1',
        click: action
    });
    let icon = $('<i>', {
        class: 'material-icons notranslate ajp-text-gray ajp-icon-48',
        text: iconText
    });

    let span = $('<span>', {
        class: 'ml-2',
        text: gettext(spanText)
    });

    button.append(icon);
    button.append(span);

    return button;
}

function createFaceAnnotationsContent(faceAnnotations) {
    let children = [];
    faceAnnotations.forEach(function(annotation) {
        let annotationIdentifier = getAnnotationIdentifier(annotation);
        let child = $('<div>', {
            class: 'd-flex align-items-center mr-2 mt-2 ajp-pebble',
            mouseenter: function() { getDisplayCorrespondingAnnotation(annotationIdentifier) },
            mouseleave: function() { getHideCorrespondingAnnotation(annotationIdentifier) },
            'data-toggle': 'popover',
            click: function(event) { toggleAnnotationLabelPopover(event, annotation, faceAnnotations); }
        });
        let anchorLink = $('<a>', {
            href: '#',
            text: annotation.label.trim()
        });
        let container = $('#ajp-modal-body').size() > 0 ? '#ajp-modal-body' : 'body';
        if (annotation.isAlbum) {
            let wrapper = $('<temporary>');
            let div = $('<div>', {
                class: 'col-auto mb-3 mt-2 px-0'
            });

            let tagButton = createTaggingButton(
                gettext('Modify existing annotations, click on an annotation to start'),
                'person_pin',
                gettext('Tag a face'),
                function() {
                    if (!window.isAnnotatingDisabled) {
                        enableAnnotations();
                        window.lastEnteredName = annotation.label.trim();
                        setTimeout(() => { $('#ajp-face-modify-rectangle-' + annotation.id).click(); }, 10);
                        $(this).parents('.popover').popover('hide');
                    }
                }
            );

            let drawAndTagButton = createTaggingButton(
                gettext("Draw a face annotation and add person's name"),
                'format_shapes',
                gettext('Draw and tag a face'),
                function() {
                    if(!window.isAnnotatingDisabled) {
                        ObjectTagger.toggleCropping();
                        window.lastEnteredName = annotation.label.trim();
                        $(this).parents('.popover').popover('hide');
                    }
                }
            );

            div.append(tagButton);
            div.append(drawAndTagButton);
            wrapper.append(div);

            let title = interpolate(gettext('Tag <i>%(personName)s</i>'), {personName: annotation.label.trim()}, true);
            child.popover({
                html: true,
                sanitize: false,
                trigger: 'manual',
                container,
                content: wrapper.children()[0],
                title
            })
        } else {
            let title = interpolate(gettext('<i>%(personName)s</i>'), {personName: annotation.label.trim()}, true);
            let request = new Request(
                annotationUrl.replace('0', annotation.id),
                {
                    method: 'GET',
                    headers: new Headers()
                }
            );
            fetch(request)
            .then(function(response) {
                return response.json();
            }).then(function(data){
                let popoverContent = $('<div>');
                if (data.user_id && data.user_name) {
                    let profileLink = $('<a>', {
                            href: userUrl.replace('0', data.user_id),
                            text: data.user_name
                        }
                    ).get(0).outerHTML;
                    popoverContent.append(interpolate(gettext('Annotation was added by %(profileLink)s'), {profileLink}, true));
                } else {
                    popoverContent.append(gettext('Automatically detected face'));
                }
                if (data.photo_count) {
                    if (popoverContent.children().length > 0) {
                        popoverContent.append($('<br>'))
                        popoverContent.append($('<br>'))
                    }
                    let photoCount = $('<span>', { text: data.photo_count }).get(0).outerHTML;
                    let photoCountText = interpolate(ngettext(
                        '%(photoCount)s photo',
                        '%(photoCount)s photos',
                        data.photo_count
                    ),
                    {photoCount},
                    true
                    );
                    popoverContent.append(photoCountText);
                }
                let tagButton = createTaggingButton(
                    gettext("Tag a face annotation with person's name"),
                    'person_pin',
                    !annotation.subjectId ? gettext('Identify person'): gettext('Edit person annotation'),
                    function() {
                        if (!window.isAnnotatingDisabled) {
                            enableAnnotations();
                            setTimeout(() => { $('#ajp-face-modify-rectangle-' + annotation.id).click(); }, 10);
                            $(this).parents('.popover').popover('hide');
                        }
                    }
                );
                popoverContent.append(tagButton);
                child.popover({
                    html: true,
                    sanitize: false,
                    trigger: 'manual',
                    container,
                    content: popoverContent,
                    title
                })
            });
        }
        let icon = $('<i>', {
            text: 'person_pin',
            class: annotation.isAlbum ? 'material-icons notranslate ajp-text-gray ajp-cursor-pointer' : 'material-icons notranslate ajp-cursor-pointer'
        });
        child.append(anchorLink).append(icon);
        children.push(child);
    });
    return children;
}

function createObjectAnnotationsContent(objectAnnotations) {
    let children = [];
    let index = 1;
    objectAnnotations.forEach(function(annotation) {
        let annotationIdentifier = getAnnotationIdentifier(annotation);
        let child = $('<a>', {
            text: annotation.label.trim(),
            class: 'd-flex align-items-center mt-2 mr-2 ajp-pebble',
            mouseenter: function() { getDisplayCorrespondingAnnotation(annotationIdentifier) },
            mouseleave: function() { getHideCorrespondingAnnotation(annotationIdentifier) },
            href: 'https://www.wikidata.org/wiki/' + annotation.wikiDataId
        });
        children.push(child);
        index += 1;
    });

    return children;
}

function getUnidentifiedPersonLabel(annotation) {
    if (annotation.age == constants.fieldValues.CHILD) {
        if (annotation.gender == constants.fieldValues.MALE) {
            return gettext('Unidentified boy');

        } else if (annotation.gender == constants.fieldValues.FEMALE) {
            return gettext('Unidentified girl');

        } else {
            return gettext('Unidentified child');
        }
    }
    if (annotation.age == constants.fieldValues.ADULT) {
        if (annotation.gender == constants.fieldValues.MALE) {
            return gettext('Unidentified adult man');

        } else if (annotation.gender == constants.fieldValues.FEMALE) {
            return gettext('Unidentified adult woman');

        } else {
            return gettext('Unidentified adult');
        }
    }
    if (annotation.age == constants.fieldValues.ELDERLY) {
        if (annotation.gender == constants.fieldValues.MALE) {
            return gettext('Unidentified elderly man');

        } else if (annotation.gender == constants.fieldValues.FEMALE) {
            return gettext('Unidentified elderly woman');

        } else {
            return gettext('Unidentified elderly person');
        }
    }
    if (annotation.gender == constants.fieldValues.MALE) {
        return gettext('Unidentified man');

    }
    if (annotation.gender == constants.fieldValues.FEMALE) {
        return gettext('Unidentified woman');
    }
    return gettext('Unidentified person')
}

function getSubjectLabel(annotation) {
    let label = '';

    if (annotation.subjectName) {
        label += (annotation.subjectName + ' ');
        if (annotation.age && annotation.age != constants.fieldValues.UNIDENTIFIED) {
            label += '(' + capitalizeFirstLetter(annotation.age) + ')';
        }
    } else {
        label = getUnidentifiedPersonLabel(annotation);
    }
    return label;
}

function collectAllLabels(detections) {
    let objects = [];
    let addedObjects = [];

    let faces = [];
    let addedSubjects = [];

    detections.forEach(function(detection) {
        let isUniqueObjectDetection = detection.wikiDataId && addedObjects.indexOf(detection.wikiDataId) === -1;

        if (isUniqueObjectDetection) {
            addedObjects.push(detection.wikiDataId);
            objects.push({
                id: detection.id,
                wikiDataId: detection.wikiDataId,
                label: getLanguageSpecificTranslation(detection.translations)
            });
        } else {
            if (detection.subjectId) {
                addedSubjects.push(detection.subjectId);
            }

            faces.push({
                id: detection.id,
                gender: detection.gender,
                isAlbum: !detection.id,
                age: detection.age,
                subjectId: detection.subjectId,
                label: getSubjectLabel(detection),
                isTagged: detection.isTagged,
                user: detection.user
            });
        }
    });

    return {
        objects: objects,
        faces: faces
    };
}

function createAnnotations(detections) {
    let personsWrapper = $('#' + constants.elements.FACE_ANNOTATIONS_ID);
    let objectsWrapper = $('#' + constants.elements.OBJECT_ANNOTATIONS_ID);
    let buttonClone = $('#add-new-subject-button').clone();
    personsWrapper.empty();
    objectsWrapper.empty();

    let allLabels = collectAllLabels(detections);
    personsWrapper.append(createFaceAnnotationsContent(allLabels.faces));
    personsWrapper.append(buttonClone);
    objectsWrapper.append(createObjectAnnotationsContent(allLabels.objects));
}
