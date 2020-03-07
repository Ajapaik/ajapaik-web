function hasScrolledToTheFurthestLeft() {
    var contentArea = document.getElementById('gallery-content');

    var scrollLocation = contentArea.scrollLeft;

    return scrollLocation === 0;
}

function hasScrolledToTheFurthestRight() {
    var contentArea = document.getElementById('gallery-content');

    var scrollLocation = contentArea.scrollLeft;
    var offsetWidth = contentArea.offsetWidth;
    var scrollWidth = contentArea.scrollWidth;

    return scrollLocation + offsetWidth === scrollWidth;
}

function setGalleryNavigations(initialized) {
    var galleryContentArea = document.getElementById('gallery-content');

    var offsetWidth = galleryContentArea.offsetWidth;
    var scrollWidth = galleryContentArea.scrollWidth;

    if (!initialized && offsetWidth >= scrollWidth) {
        $('#right-button').css('visibility', 'hidden');
        $('#left-button').css('visibility', 'hidden');
        initialized = true;
    } else if (!initialized) {
        $('#right-button').css('visibility', '');
        initialized = true;

    }

    return initialized;
}

function addGalleryLeftAndRightButtonEventHandlers() {
    $('#left-button').click(function () {
        if (!hasScrolledToTheFurthestLeft()) {
            $('#right-button').css('visibility', '');

            $('#gallery-content').animate({
                scrollLeft: '-=110px'
            }, 800, function () {
                if (hasScrolledToTheFurthestLeft()) {
                    $('#left-button').css('visibility', 'hidden');
                }
            });
        }
    });

    $('#right-button').click(function () {
        if (!hasScrolledToTheFurthestRight()) {
            $('#left-button').css('visibility', '');

            $('#gallery-content').animate({
                scrollLeft: '+=110px'
            }, 800, function () {
                if (hasScrolledToTheFurthestRight()) {
                    $('#right-button').css('visibility', 'hidden');
                }
            });
        }
    });
}
