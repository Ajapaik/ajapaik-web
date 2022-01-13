'use strict';

// FIXME: Copied from addanother.js because of how we implemented async popup form loading
var idToWindowName = function (text) {
  text = text.replace(/\./g, '__dot__');
  text = text.replace(/-/g, '__dash__');
  text = text.replace(/\[/g, '__braceleft__');
  text = text.replace(/]/g, '__braceright__');
  return text;
};

function showAddAnotherPopup(triggeringLink) {
  let name = triggeringLink.attr('id').replace(/^add_/, '');
  name = idToWindowName(name);
  let href = triggeringLink.attr('href');

  if (href.indexOf('?') === -1) {
    href += '?';
  }

  href += '&winName=' + name;

  const height = 500;
  const width = 800;
  const left = screen.width / 2 - width / 2;
  const top = screen.height / 2 - height / 2;
  const win = window.open(
    href,
    name,
    'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, copyhistory=no, width=' +
      width +
      ', height=' +
      height +
      ', top=' +
      top +
      ', left=' +
      left
  );
  let subjectName = '';
  const yourLabsOverlay = $('#yourlabs_overlay');

  function removeOverlay() {
    if (win.closed) {
      yourLabsOverlay.remove();
      document
        .querySelector('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
        .slim.open();
      setTimeout(() => {
        document
          .querySelector('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
          .slim.search(subjectName);
      }, 100);
    } else {
      if (win.window && win.window.$) {
        subjectName = win.window.$('.form-group input#id_name').val();
      }
      setTimeout(removeOverlay, 500);
    }
  }

  $('body').append('<div id="yourlabs_overlay"></div>');
  yourLabsOverlay.click(function () {
    win.close();
    $(this).remove();
  });

  setTimeout(removeOverlay, 1500);

  win.focus();

  return false;
}

function initializeAddNewPersonOpeningAPopup() {
  $(document).on(
    'click',
    '#' + constants.elements.ADD_NEW_SUBJECT_LINK_ID,
    function (e) {
      e.preventDefault();
      e.stopPropagation();
      showAddAnotherPopup($(this));
    }
  );
}

$(document).ready(function () {
  initializeAddNewPersonOpeningAPopup();
});
