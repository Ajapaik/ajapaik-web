async function handleErrors(response) {
    const data = await response.json();
    if (data.error) {
        throw data.error;
    }
    return data.message;
}

function submitCategorySuggestion(photoIds, isModal) {
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
    .then(handleErrors)
    .then(function(message) {
        if (isModal) {
            updatePhotoScene();
            $('#ajp-categorize-scene-button').not(this).popover('hide');
            $('#ajp-categorize-scene-button').popover('dispose');
        } else {
            $('#ajp-photo-selection-categorize-scenes-button').not(this).popover('hide');
        }
        $.notify(message, {type: 'success'});
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
        viewpointElevation = 'Raised'
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

    scene = buttonId === 'interior-button'
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