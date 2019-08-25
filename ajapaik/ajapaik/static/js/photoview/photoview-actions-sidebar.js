'use strict';

$(document).ready(function () {
    function getShareLinkContent(label, url, linkId, customStyle) {
        var wrapper = $('<div>', {
            role: 'menuitem',
            tabindex: '-1',
            style: customStyle
        });

        var link = $('<a>', {
            id: linkId,
            href: url,
            target: '_blank'
        });

        var labelWrapper = $('<span>', {
            style: 'font-weight: bold;'
        });

        return wrapper
            .append(labelWrapper
                .append(label + ': ')
            )
            .append(link
                .append(url)
            );
    }

    function createShareImageWithoutRephotoLink(shareButton) {
        var label = gettext(constants.translations.photoView.links.SHARE_PHOTO);
        var url = shareButton.data('url');

        return getShareLinkContent(label, url);
    }

    function createShareImageWithRephotoLink(shareButton) {
        var label = gettext(constants.translations.photoView.links.SHARE_PHOTO_WITH_RE_PHOTO);
        var url = shareButton.data('rephoto-url');
        var customStyle = 'padding-top: 10px;';

        if (url) {
            return getShareLinkContent(label, url, constants.elements.RE_PHOTO_SHARE_LINK_ID, customStyle);
        }
    }

    function getPopoverContent(shareButton) {
        var linkToPhoto = createShareImageWithoutRephotoLink(shareButton);
        var linkToPhotoWithRephoto = createShareImageWithRephotoLink(shareButton);

        var wrapper = $('<div>');

        return wrapper
            .append(linkToPhoto)
            .append(linkToPhotoWithRephoto);
    }

    function initializeShareButtonPopover() {
        var shareButton = $('#ajapaik-sharing-dropdown-button');
        var popoverContent = getPopoverContent(shareButton);

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