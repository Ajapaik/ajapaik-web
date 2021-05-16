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
    if ((!window.openPersonPopoverLabelIds || !window.openPersonPopoverLabelIds.includes(annotationIdentifier)) &&
        (!window.openObjectPopoverLabelIds || !window.openObjectPopoverLabelIds.includes(annotationIdentifier))) {
        let correspondingAnnotations = getCorrespondingAnnotations(annotationIdentifier);
        correspondingAnnotations.css({visibility: 'hidden'});
    }
}

function togglePersonAnnotationLabelPopover(event, annotation, faceAnnotations) {
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
                displayAnnotations(true, false);
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

function toggleObjectAnnotationLabelPopover(event, annotation) {
    event.preventDefault();
    if (!window.isAnnotatingDisabled) {
        let popoverTarget = $(event.target).data("bs.popover") === undefined
            ? $(event.target).parents('[data-toggle="popover"]')
            : $(event.target);
        
        if (popoverTarget.attr('aria-describedby') == undefined) {
            $('.ajp-object-label-popover').not('[id=' + popoverTarget.attr('aria-describedby') +']').popover('hide');
            popoverTarget.popover('show');
            $('[id=' + popoverTarget.attr('aria-describedby') + ']').addClass('ajp-object-label-popover');
            window.openObjectPopoverLabelIds = [getAnnotationIdentifier(annotation)];
            $('#ajp-object-modify-rectangle-' + annotation.id).css('visibility', 'visible');
        } else {
            $('.ajp-object-label-popover').popover('hide');
            window.openObjectPopoverLabelIds = [];
            hideAnnotationsWithoutOpenPopover();
        }
    }
}

function createIconButton(title, iconText, spanText, action) {
    let button = $('<button>', {
        title,
        class: 'btn btn-light d-flex align-items-center w-100 my-1',
        click: action
    });
    let icon = $('<i>', {
        class: 'material-icons notranslate ajp-text-gray ajp-icon-36',
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

function createAlbumLabelPopoverContent(annotation, child, container) {
    let wrapper = $('<temporary>');
    let div = $('<div>', {
        class: 'col-auto mb-3 mt-2 px-0'
    });

    let tagButton = createIconButton(
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

    let drawAndTagButton = createIconButton(
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

    let viewAlbumButton = createIconButton(
        gettext("Open album"),
        'photo_album',
        gettext('Open album'),
        function() {
            window.open('/?album=' + annotation.subjectId, '_blank');
        }
    )

    div.append(tagButton);
    div.append(drawAndTagButton);
    div.append(viewAlbumButton);
    wrapper.append(div);

    let title = interpolate(gettext('Tag <em>%(personName)s</em>'), {personName: annotation.label.trim()}, true);
    child.popover({
        html: true,
        sanitize: false,
        trigger: 'manual',
        container,
        content: wrapper.children()[0],
        title
    })

    return child;
}

function createAnnotationLabelPopoverContent(annotation, child, container) {
    let title = interpolate('<em>%(personName)s</em>', {personName: annotation.label.trim()}, true);
    let request = new Request(
        faceAnnotationUrl.replace('0', annotation.id),
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
            popoverContent.append($('<span>', { text: gettext('Automatically detected face')}));
        }
        if (data.photo_count) {
            if (popoverContent.children().length > 0) {
                popoverContent.append($('<br>'))
                popoverContent.append($('<br>'))
            }
            let photoCount = $('<span>', { text: data.photo_count }).get(0).outerHTML;
            let photoCountText = interpolate(ngettext(
                '%(photoCount)s picture',
                '%(photoCount)s pictures',
                data.photo_count
            ),
            {photoCount},
            true
            );
            popoverContent.append(photoCountText);
        }
        let tagButton = createIconButton(
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

        if (annotation.subjectId) {
            let viewAlbumButton = createIconButton(
                gettext("Open album"),
                'photo_album',
                gettext('Open album'),
                function() {
                    window.open('/?album=' + annotation.subjectId, '_blank');
                });
            popoverContent.append(viewAlbumButton);
        }

        child.popover({
            html: true,
            sanitize: false,
            trigger: 'manual',
            container,
            content: popoverContent,
            title
        })
    });

    return child;
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
            click: function(event) { togglePersonAnnotationLabelPopover(event, annotation, faceAnnotations); }
        });
        let anchorLink = $('<a>', {
            href: '#',
            text: annotation.label.trim()
        });
        let container = $('#ajp-modal-body').size() > 0 ? '#ajp-modal-body' : 'body';
        let personPinClass = 'material-icons notranslate ajp-cursor-pointer';
        if (annotation.isAlbum) {
            child = createAlbumLabelPopoverContent(annotation, child, container);
            personPinClass += ' ajp-text-gray';
        } else {
            child = createAnnotationLabelPopoverContent(annotation, child, container);
        }
        let icon = $('<i>', {
            text: 'person_pin',
            class: personPinClass
        });
        child.append(anchorLink).append(icon);
        children.push(child);
    });
    return children;
}

function createObjectAnnotationsContent(objectAnnotations) {
    let children = [];
    let container = $('#ajp-modal-body').size() > 0 ? '#ajp-modal-body' : 'body';
    objectAnnotations.forEach(function(annotation) {
        let annotationIdentifier = getAnnotationIdentifier(annotation);
        let child = $('<a>', {
            href: '#',
            text: annotation.label.trim(),
            class: 'd-flex align-items-center mt-2 mr-2 ajp-pebble',
            mouseenter: function() { getDisplayCorrespondingAnnotation(annotationIdentifier) },
            mouseleave: function() { getHideCorrespondingAnnotation(annotationIdentifier) },
            'data-toggle': 'popover',
            click: function(event) { toggleObjectAnnotationLabelPopover(event, annotation); }
        });

        let request = new Request(
            objectAnnotationUrl.replace('0', annotation.id),
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
                popoverContent.append(gettext('Automatically detected object'));
            }
            let openWikiDataButton = createIconButton(
                gettext("View object on Wikidata"),
                'open_in_new',
                gettext('View object on Wikidata'),
                function() {
                    window.open('https://www.wikidata.org/wiki/' + annotation.wikiDataId, '_blank');
                    $(this).parents('.popover').popover('hide');
                }
            );
            popoverContent.append(openWikiDataButton);

            child.popover({
                html: true,
                sanitize: false,
                trigger: 'manual',
                container,
                content: popoverContent,
                title: annotation.label.trim()
            });
        });

        children.push(child);
    });

    return children;
}

function getUnidentifiedPersonLabel(annotation) {
    let label = 'Unidentified';
    if (annotation.age && annotation.age == constants.fieldValues.ageGroups.CHILD) {
        if(annotation.gender == constants.fieldValues.genders.MALE) {
            label += ' boy';
        } else if (annotation.gender == constants.fieldValues.genders.FEMALE) {
            label += ' girl';
        } else {
            label += ' child';
        }
    } else {
        if (annotation.age == constants.fieldValues.ageGroups.ADULT) {
            label += ' adult';
        } else if (annotation.age == constants.fieldValues.ageGroups.ELDERLY) {
            label += ' elderly';
        }
        if (annotation.gender == constants.fieldValues.genders.MALE) {
            label += ' man';
        } else if (annotation.gender == constants.fieldValues.genders.FEMALE) {
            label += ' woman';
        } else {
            label += ' person';
        }
    }
    label = gettext(label.trim());

    return label.substring(0,1).toUpperCase() + label.substring(1);
}

function getSubjectLabel(annotation) {
    let label = '';

    if (annotation.subjectName) {
        label += (annotation.subjectName + ' ');
        if (annotation.age && annotation.age != constants.fieldValues.common.UNSURE) {
            label += '(' + gettext(capitalizeFirstLetter(annotation.age)) + ')';
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
