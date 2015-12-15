(function () {
    'use strict';
    $(document).ready(function () {
        var rephotoContainer = $('#tan-rephoto-container'),
            originalImage = $('#tan-rephoto-original-image');
        originalImage.one('load', function () {
            rephotoContainer.css('max-width', originalImage.width());
            rephotoContainer.twentytwenty();
        }).each(function () {
            if (this.complete) {
                $(this).load();
            }
        });
    });
}());