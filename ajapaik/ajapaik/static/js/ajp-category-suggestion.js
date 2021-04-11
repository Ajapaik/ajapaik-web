function submitCategorySuggestion(photoIds, isMultiSelect) {
    $('#ajp-loading-overlay').show();
    return fetch(photoSceneUrl, {
        method: 'POST',
        beforeSend : function(xhr) {
            xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        },
        headers: {
            'Content-Type': 'application/json',

        },
        body: JSON.stringify({
            photoIds,
            scene,
            viewpointElevation
        })
    
    })
    .then(window.handleErrors)
    .then(function(data) {
        if (!isMultiSelect) {
            $('#ajp-categorize-scene').not(this).popover('hide');
            $('#ajp-categorize-scene').popover('dispose');
            updatePhotoSuggestions();
        } else {
            $('#ajp-photo-selection-categorize-scenes-button').not(this).popover('hide');
        }
        $.notify(data.message, {type: 'success'});
        $('#ajp-loading-overlay').hide();
    }).catch((error) => {
        $('#ajp-loading-overlay').hide();
        $.notify(error, {type: 'danger'});
    });
};

function clickViewpointElevationCategoryButton(buttonId) {
    $('#send-suggestion-button').prop("disabled", false);

    let otherButtonIds = [];

    if (buttonId === 'aerial-button') {
        viewpointElevation = 'Aerial';
    } else if (buttonId === 'raised-button') {
        viewpointElevation = 'Raised';
    } else if (buttonId === 'ground-button') {
        viewpointElevation = 'Ground';
    }
    
    if (viewpointElevation === 'Aerial') {
        otherButtonIds = ['#ground-button', '#raised-button'];
    } else if (viewpointElevation === 'Raised') {
        otherButtonIds = ['#ground-button', '#aerial-button'];
    } else if (viewpointElevation === 'Ground') {
        otherButtonIds = ['#raised-button', '#aerial-button'];
    }

    otherButtonIds.forEach(function(id) {
        if(!$(id).hasClass('btn-outline-primary')) {
            $(id).addClass('btn-light');
        }
        if($(id).hasClass('btn-outline-primary')) {
            $(id).removeClass('btn-outline-primary');
        }
        if($(id).hasClass('btn-outline-dark')) {
            $(id).removeClass('btn-outline-dark');
        }
    });

    $('#' + buttonId).addClass('btn-outline-primary');
    $('#' + buttonId).removeClass('btn-outline-dark');
    $('#' + buttonId).removeClass('btn-light');
};

function clickSceneCategoryButton(buttonId) {
    $('#send-suggestion-button').prop("disabled", false);

    let scene = buttonId === 'interior-button'
        ? 'Interior'
        : 'Exterior';
    let otherButtonId = scene === 'Interior'
        ? '#exterior-button'
        : '#interior-button';

    if(!$(otherButtonId).hasClass('btn-light')) {
        $(otherButtonId).addClass('btn-light');
    }

    if ($(otherButtonId).hasClass('btn-outline-primary')) {
        $(otherButtonId).removeClass('btn-outline-primary');
    }

    if ($(otherButtonId).hasClass('btn-outline-dark')) {
        $(otherButtonId).removeClass('btn-outline-dark');
    }

    $('#' + buttonId).addClass('btn-outline-primary');
    $('#' + buttonId).removeClass('btn-outline-dark');
    $('#' + buttonId).removeClass('btn-light');
};