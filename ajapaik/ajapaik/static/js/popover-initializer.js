'use strict';

function initializeClosingPopoverWhenClickingOutsideOfPopover() {
    $('html').on('click', function(e) {
        if (typeof $(e.target).data('is-detection-rectangle') === 'undefined' && !$(e.target).parents().is('.popover')) {
            $('[data-is-detection-rectangle]').popover('hide');
        }
    });
}

$(document).ready(initializeClosingPopoverWhenClickingOutsideOfPopover);
