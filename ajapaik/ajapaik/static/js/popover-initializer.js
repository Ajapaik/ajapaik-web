'use strict';

function initializeClosingPopoverWhenClickingOutsideOfPopover() {
    $('html').on('click', function(e) {
        var hasNotClickedDetectionRectangle = typeof $(e.target).data('is-detection-rectangle') === 'undefined' ;
        var hasNotClickedRegularPopoverEnablingElement = typeof $(e.target).data('is-popover-target') === 'undefined';

        if (!$(e.target).parents().is('.popover')) {
            if (hasNotClickedDetectionRectangle) {
                $('[data-is-detection-rectangle]').popover('hide');
            }

            if (hasNotClickedRegularPopoverEnablingElement) {
                $('#ajapaik-sharing-dropdown-button').popover('hide');
            }
        }
    });
}

$(document).ready(initializeClosingPopoverWhenClickingOutsideOfPopover);
