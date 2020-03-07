'use strict';

// FIXME: Copied from addanother.js because of how we implemented async popup form loading
var idToWindowName = function (text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    text = text.replace(/\[/g, '__braceleft__');
    text = text.replace(/\]/g, '__braceright__');
    return text;
};

function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.attr('id').replace(/^add_/, '');
    name = idToWindowName(name);
    var href = triggeringLink.attr('href');

    if (href.indexOf('?') === -1) {
        href += '?';
    }

    href += '&winName=' + name;

    var height = 500;
    var width = 800;
    var left = (screen.width / 2) - (width / 2);
    var top = (screen.height / 2) - (height / 2);
    var win = window.open(href, name, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, copyhistory=no, width=' + width + ', height=' + height + ', top=' + top + ', left=' + left);

    function removeOverlay() {
        if (win.closed) {
            $('#yourlabs_overlay').remove();
        } else {
            setTimeout(removeOverlay, 500);
        }
    }

    $('body').append('<div id="yourlabs_overlay"></div>');
    $('#yourlabs_overlay').click(function () {
        win.close();
        $(this).remove();
    });

    setTimeout(removeOverlay, 1500);

    win.focus();

    return false;
}

function initializeAddNewPersonOpeningAPopup() {
    $(document).on('click', '#' + constants.elements.ADD_NEW_SUBJECT_LINK_ID, function (e) {
        e.preventDefault();
        e.stopPropagation();
        // Workaround for getting data out of now closed programmatically generated iframe
        // window.docCookies.setItem('ajapaik_last_added_subject_id', null,
        //     'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
        showAddAnotherPopup($(this));
    });
}

$(document).ready(function() {
    initializeAddNewPersonOpeningAPopup();
});
