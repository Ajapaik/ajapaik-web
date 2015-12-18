(function () {
    'use strict';
    $(document).ready(function () {
        $('#sortable').hide();
        var targets = $('#id_photos-deck').find('span');
        targets.hover(function () {
            var $this = $(this),
                id = $this.data('value');
            $this.popover({
                content: id,
                trigger: 'hover'
            });
        });
        $('#id_grouped').change(function () {
            if ($(this).is(':checked')) {
                $('#sortable').show();
            } else {
                $('#sortable').hide();
            }
        });
    });
}());