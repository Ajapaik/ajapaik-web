$(document).ready(function () {
    var initialized = false;
    var rephotos = $('#rephotos');

    $('[data-image-preview-rephotos="true"]').click(function (event) {
        var clickedImagePreview = $(event.target);
        var newRephotoUrl = clickedImagePreview.data('full-image-url');
        var fullScreenRephotoUrl = clickedImagePreview.data('full-screen-url');
        var rephotoShareUrl = clickedImagePreview.data('share-url');

        $('#ajapaik-photoview-rephoto').attr('src', newRephotoUrl);
        $('#ajapaik-rephoto-full-screen-image').attr('data-src', fullScreenRephotoUrl);

        $('#ajapaik-sharing-dropdown-button').data('rephoto-url', rephotoShareUrl);
        $('#' + constants.elements.RE_PHOTO_SHARE_LINK_ID).html(rephotoShareUrl);
    });

    rephotos.mouseenter(function () {
        $('#ajapaik-photoview-rephoto-selection').css('display', '');
        initialized = setGalleryNavigations(initialized);
    });

    rephotos.mouseleave(function () {
        $('#ajapaik-photoview-rephoto-selection').css('display', 'none');
    });

    addGalleryLeftAndRightButtonEventHandlers();

    $(window).on('resize', function () {
        initialized = false;
    });
});