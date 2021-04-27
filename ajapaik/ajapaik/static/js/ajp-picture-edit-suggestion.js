function submitPictureEditSuggestion(photoIds, isSelection) {
    $('#ajp-loading-overlay').show();
    let body = undefined

    if (!isSelection) {
        if (newPhotoRotationDegrees === 'undefined' || newPhotoRotationDegrees === undefined) {
            newPhotoRotationDegrees = 0;
        }
        if (photoRotationDegreesConsensus === 'undefined' || photoRotationDegreesConsensus === undefined) {
            photoRotationDegreesConsensus = 0;
        }
        if (newIsPhotoFlipped === 'undefined') {
            newIsPhotoFlipped = false;
        }
        if (newIsPhotoInverted === 'undefined') {
            newIsPhotoInverted = false;
        }
        body = JSON.stringify({
            photoIds,
            flip: newIsPhotoFlipped,
            invert: newIsPhotoInverted,
            rotated: (photoRotationDegreesConsensus + newPhotoRotationDegrees) % 360
        });
    } else {
        body = JSON.stringify({
            photoIds,
            flip: window.selectionPhotoFlipped,
            invert: window.selectionPhotoInverted,
            rotated: window.selectionPhotoRotationDegrees
        });
    }

    return fetch(photoAppliedOperationsUrl, {
        method: 'POST',
        beforeSend : function(xhr) {
            xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        },
        headers: {
            'Content-Type': 'application/json'
        },
        body

    })
    .then(window.handleErrors)
    .then(function(data) {
        $.notify(data.message, {type: 'success'});
        if (window.previouslyEditedPhotoIds && window.previouslyEditedPhotoIds.length > 0) {
            photoIds.forEach(id => {
                if (window.previouslyEditedPhotoIds.indexOf(id) === -1) {
                    window.previouslyEditedPhotoIds.push(id);
                }
            });
        } else {
            window.previouslyEditedPhotoIds = photoIds;
        }

        localStorage.setItem("previouslyEditedPhotoIds", JSON.stringify(window.previouslyEditedPhotoIds));

        if (!isSelection) {
            $('#ajp-edit-picture').not(this).popover('hide');
            $('#ajp-edit-picture').popover('dispose');
            updatePhotoAppliedOperations();
        } else {
            $('#ajp-photo-selection-edit-pictures-button').not(this).popover('hide');
        }

        window.lastRotateWas90 = data.rotated_by_90;

        window.refreshUpdatedImage('#ajp-modal-photo');
        window.refreshUpdatedImage('#ajp-photoview-main-photo');
        window.refreshUpdatedImage('#ajp-fullscreen-image');
        photoIds.forEach(id => {
            window.refreshUpdatedImageLight('img[data-id=' + id + ']');
            window.refreshUpdatedImageLight('a[data-id=' + id + '].ajp-photo-selection-thumbnail-link > img');
        });
        $('#ajp-fullscreen-image-wrapper').removeClass();
        $('#ajp-fullscreen-image').addClass('lasyloaded');
        window.photoModalCurrentPhotoInverted = false;
        window.photoModalCurrentPhotoFlipped = false;
        if (typeof currentPhoto !== 'undefined' && currentPhoto.flip) {
            currentPhoto.flip = !currentPhoto.flip;
        }
        if (window.lastRotateWas90) {
            let temporary = window.currentPhotoOriginalHeight;
            window.currentPhotoOriginalHeight = window.currentPhotoOriginalWidth;
            window.currentPhotoOriginalWidth = temporary;
        }
        if (!isSelection) {
            newPhotoRotationDegrees = 'undefined';
            newIsPhotoFlipped = 'undefined';
            refreshAnnotations();
            enableAnnotations();
        } else {
            window.selectionPhotoFlipped = false;
            window.selectionPhotoInverted = false;
            window.selectionPhotoRotationDegrees = 0;
        }

        $('#ajp-loading-overlay').hide();
    }).catch((error) => {
        $('#ajp-loading-overlay').hide();
        $.notify(error, {type: 'danger'});
    });
};

function clickPhotoEditButton(buttonId, noop) {
    if (buttonId === 'flip-button') {
        if (!noop) {
            if (newIsPhotoFlipped !== 'undefined') {
                newIsPhotoFlipped = !newIsPhotoFlipped;
            } else {
                newIsPhotoFlipped = true;
            }
        } else {
            window.selectionPhotoFlipped = !window.selectionPhotoFlipped;
        }
        $('#' + buttonId).toggleClass('btn-outline-primary');
        $('#' + buttonId).toggleClass('btn-light');
        flipPhoto();
    } else if (buttonId === 'invert-button') {
        if (!noop) {
            if (newIsPhotoInverted !== 'undefined') {
                newIsPhotoInverted = !newIsPhotoInverted;
            } else {
                newIsPhotoInverted = true;
            }
        } else {
            window.selectionPhotoInverted = !window.selectionPhotoInverted;
        }
        $('#' + buttonId).toggleClass('btn-outline-primary');
        $('#' + buttonId).toggleClass('btn-light');
        invertPhoto();
    } else if (buttonId === 'rotate-button') {
        if (!noop) {
            let photoContainer = isPhotoview ? $('#ajp-photoview-main-photo') : $('#ajp-modal-photo');
            if (photoContainer && photoContainer.hasClass('ajp-photo-flipped')) {
                if (newPhotoRotationDegrees !== 'undefined' && newPhotoRotationDegrees !== undefined) {
                    newPhotoRotationDegrees = (newPhotoRotationDegrees - 90) % 360;
                } else {
                    newPhotoRotationDegrees = 270;
                }
                if (newPhotoRotationDegrees < 0) {
                    newPhotoRotationDegrees += 360;
                }
                if (newPhotoRotationDegrees == 0) {
                    $('#' + buttonId).addClass('btn-light');
                    $('#' + buttonId).removeClass('btn-outline-primary');
                }
                if (newPhotoRotationDegrees == 270) {
                    $('#' + buttonId).removeClass('btn-light');
                    $('#' + buttonId).addClass('btn-outline-primary');
                }
                rotatePhoto(true);
            } else {
                if (newPhotoRotationDegrees !== 'undefined' && newPhotoRotationDegrees !== undefined) {
                    newPhotoRotationDegrees = (newPhotoRotationDegrees + 90) % 360;
                } else {
                    newPhotoRotationDegrees = 90;
                }
                if (newPhotoRotationDegrees == 0) {
                    $('#' + buttonId).addClass('btn-light');
                    $('#' + buttonId).removeClass('btn-outline-primary');
                }

                if (newPhotoRotationDegrees == 90) {
                    $('#' + buttonId).removeClass('btn-light');
                    $('#' + buttonId).addClass('btn-outline-primary');
                }
                rotatePhoto(false);
            }
        } else {
            window.selectionPhotoRotationDegrees += 90;
            window.selectionPhotoRotationDegrees = window.selectionPhotoRotationDegrees % 360;

            if (window.selectionPhotoRotationDegrees == 0) {
                $('#' + buttonId).addClass('btn-light');
                $('#' + buttonId).removeClass('btn-outline-primary');
                $('#' + buttonId + ' > i').removeClass('rotate270');
            }
            if (window.selectionPhotoRotationDegrees == 90) {
                $('#' + buttonId).removeClass('btn-light');
                $('#' + buttonId).addClass('btn-outline-primary');
                $('#' + buttonId + ' > i').addClass('rotate90');
            }
            if (window.selectionPhotoRotationDegrees == 180) {
                $('#' + buttonId + ' > i').removeClass('rotate90');
                $('#' + buttonId + ' > i').addClass('rotate180');
            }
            if (window.selectionPhotoRotationDegrees == 270) {
                $('#' + buttonId + ' > i').removeClass('rotate180');
                $('#' + buttonId + ' > i').addClass('rotate270');
            }
        }
    }

    if (!noop) {
        if (newIsPhotoFlipped === isPhotoFlipped && newIsPhotoInverted === isPhotoInverted && ((photoRotationDegreesConsensus + newPhotoRotationDegrees) % 360)  === photoRotationDegrees) {
            $('#send-edit-button').prop("disabled", true);
        } else {
            $('#send-edit-button').prop("disabled", false);
        }
    }
};

function rotatePhoto(reverse) {
    let photoContainer = $('#ajp-modal-photo');
    let photoFullScreenContainer = $('#ajp-fullscreen-image-wrapper');
    if (isPhotoview) {
        photoContainer = $('#ajp-photoview-main-photo');
    }
    let photoContainerPadding = (1 - photoContainer.height() / photoContainer.width()) * 50;

    disableAnnotations();

    if (!reverse) {
        if (photoContainer.hasClass('rotate90')) {
            photoContainer.removeClass('rotate90').addClass('rotate180');
            photoContainer.removeAttr('style');
            photoFullScreenContainer.removeClass('rotate90').addClass('rotate180');
        }
        else if (photoContainer.hasClass('rotate180')) {
            if (photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.removeClass('rotate180').addClass('rotate270');
            photoFullScreenContainer.removeClass('rotate180').addClass('rotate270');

        }
        else if (photoContainer.hasClass('rotate270')) {
            photoContainer.removeClass('rotate270');
            photoContainer.removeAttr('style');
            photoFullScreenContainer.removeClass('rotate270');
            enableAnnotations();
        }
        else {
            if (photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.addClass('rotate90');
            photoFullScreenContainer.addClass('rotate90');
        }
    } else {
        if (photoContainer.hasClass('rotate90')) {
            photoContainer.removeClass('rotate90');
            photoContainer.removeAttr('style');
            photoFullScreenContainer.removeClass('rotate90');
            enableAnnotations();
        }
        else if (photoContainer.hasClass('rotate180')) {
            if (photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.removeClass('rotate180').addClass('rotate90');
            photoFullScreenContainer.removeClass('rotate180').addClass('rotate90');

        }
        else if (photoContainer.hasClass('rotate270')) {
            photoContainer.removeClass('rotate270').addClass('rotate180');
            photoContainer.removeAttr('style');
            photoFullScreenContainer.removeClass('rotate270').addClass('rotate180');;
        }
        else {
            if (photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.addClass('rotate270');
            photoFullScreenContainer.addClass('rotate270');
        }
    }
};

function invertPhoto () {
    $('#ajp-game-modal-photo').toggleClass('ajp-photo-inverted');
    let photoContainer = $('#ajp-modal-photo'),
        fullScreenImage = $('#ajp-fullscreen-image');
    if (isPhotoview) {
        photoContainer = $('#ajp-photoview-main-photo');
    }
    if (photoContainer && photoContainer.hasClass('ajp-photo-inverted')) {
        photoContainer.removeClass('ajp-photo-inverted');
    } else if (photoContainer) {
        photoContainer.addClass('ajp-photo-inverted');
    }
    if (fullScreenImage && fullScreenImage.hasClass('ajp-photo-inverted')) {
        fullScreenImage.removeClass('ajp-photo-inverted');
    } else if (fullScreenImage) {
        fullScreenImage.addClass('ajp-photo-inverted');
    }
    window.photoModalCurrentPhotoInverted = !window.photoModalCurrentPhotoInverted;
}

function flipPhoto () {
    if (typeof currentPhoto !== 'undefined' && currentPhoto.flip) {
        currentPhoto.flip = !currentPhoto.flip;
    }
    $('#ajp-game-modal-photo').toggleClass('ajp-photo-flipped');

    let photoContainer = $('#ajp-modal-photo'),
        fullScreenImage = $('#ajp-fullscreen-image');
    if (isPhotoview) {
        photoContainer = $('#ajp-photoview-main-photo');
    }
    if (photoContainer && photoContainer.hasClass('ajp-photo-flipped')) {
        photoContainer.removeClass('ajp-photo-flipped');
    } else if (photoContainer) {
        photoContainer.addClass('ajp-photo-flipped');
    }
    if (fullScreenImage && fullScreenImage.parent().hasClass('ajp-photo-flipped')) {
        fullScreenImage.parent().removeClass('ajp-photo-flipped');
    } else if (fullScreenImage) {
        fullScreenImage.parent().addClass('ajp-photo-flipped');
    }
    mirrorDetectionAnnotations();
    window.photoModalCurrentPhotoFlipped = !window.photoModalCurrentPhotoFlipped;
};