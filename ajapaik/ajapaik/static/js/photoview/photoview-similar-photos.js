$(document).ready(function () {
    var initialized = false;
    var similarPhotos = $('#similar-photos');

    $('[data-image-preview="true"]').click(function (event) {
        var similarPhotoLargeView = $('#similar-photo-large-view');

        var clickedImagePreview = $(event.target);

        var newSimilarImageUrl = clickedImagePreview.data('full-image-url');
        var newSimilarImageAlt = clickedImagePreview.attr('alt');
        var newSimilarImageTitle = clickedImagePreview.attr('title');
        var newSimilarImageUrlToView = clickedImagePreview.data('image-link');

        similarPhotoLargeView.attr('src', newSimilarImageUrl);
        similarPhotoLargeView.attr('alt', newSimilarImageAlt);
        similarPhotoLargeView.attr('title', newSimilarImageTitle);

        $('#similar-photo-link').attr('href', newSimilarImageUrlToView);
    });

    similarPhotos.mouseenter(function () {
        $('#similar-photo-selection').css('display', '');
        initialized = setGalleryNavigations(initialized);
    });

    similarPhotos.mouseleave(function () {
        $('#similar-photo-selection').css('display', 'none');
    });

    addGalleryLeftAndRightButtonEventHandlers();

    $(window).on('resize', function () {
        initialized = false;
    });
});