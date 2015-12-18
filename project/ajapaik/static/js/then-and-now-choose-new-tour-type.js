(function () {
    'use strict';
    $(document).ready(function () {
        var randomCount = $('#id_random_count').parent();
        randomCount.hide();
        $('#id_tour_type').change(function () {
            if (parseInt($(this).val(), 10) === 2) {
                randomCount.show();
            } else {
                randomCount.hide();
            }
        });
    });
}());