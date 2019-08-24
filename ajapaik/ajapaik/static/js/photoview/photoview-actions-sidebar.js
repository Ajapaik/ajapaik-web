'use strict';

$(document).ready(function () {
    function getContent(url) {
        var wrapper = $('<div>', {
            id: 'ajapaik-grab-link',
            role: 'menuitem',
            tabindex: '-1'
        });

        var link = $('<a>', {
            href: url,
            target: '_blank'
        });

        return wrapper
            .append(link
                .append(url)
            );
    }

    function initializeShareButtonPopover() {
        var shareButton = $('#ajapaik-sharing-dropdown-button');
        var link = shareButton.data('url');
        var popoverContent = getContent(link);

        shareButton.popover({
            container: 'body',
            html: true,
            placement: 'right',
            trigger: 'click',
            content: function () {
                return popoverContent;
            }
        });
    }

    initializeShareButtonPopover();
});