(function () {
    'use strict';
    $(document).ready(function () {
        $('#sortable').hide();
        $(document).on('mouseover', $('#id_photos-deck span'), function (e) {
            var $target = $(e.target),
                id;
            if ($target.attr('data-value')) {
                id = $target.data('value');
                $target.popover({
                    content: '<img class="img-responsive" src="/photo-thumb/' + id + '/400/">',
                    html: true,
                    placement: 'auto top',
                    trigger: 'hover'
                }).popover('show');
            }
        });
        // TODO: shut down popover when deleting photo, otherwise the image lingers
        var groupedCheckbox = $('#id_grouped');
        if (groupedCheckbox.is(':checked')) {
            $('#sortable').show();
        }
        groupedCheckbox.change(function () {
            if ($(this).is(':checked')) {
                $('#sortable').show();
            } else {
                $('#sortable').hide();
            }
        });
        $(document).on('click', $('#id_photos-deck').find('span').find('remove'), function () {
            $('.popover').remove();
        });
    });
}());