(function () {
    'use strict';
    /* global deleteTourURL */
    /* global alert */
    /* global gettext */
    /* global docCookies */
    /* global confirm */
    $(document).ready(function () {
        $('.tan-delete-tour-button').click(function () {
            if (confirm(gettext('Are you sure?'))) {
                var $this = $(this),
                    tourCountElement = $('#tan-my-tours-count'),
                    participatedCountElement = $('#tan-my-participated-count'),
                    viewedCountElement = $('#tan-my-viewed-count');
                $.ajax({
                    method: 'POST',
                    url: deleteTourURL,
                    data: {
                        tourId: $this.data('id'),
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function () {
                        $this.parent().remove();
                        $('#tan-my-tours-tour-viewed-' + $this.data('id')).remove();
                        $('#tan-my-tours-tour-participated-' + $this.data('id')).remove();
                        tourCountElement.html(parseInt(tourCountElement.html(), 10) - 1);
                        participatedCountElement.html(parseInt(participatedCountElement.html(), 10) - 1);
                        viewedCountElement.html(parseInt(viewedCountElement.html(), 10) - 1);
                    },
                    error: function () {
                        alert(gettext('Cannot delete tour, has rephotos or does not belong to you.'));
                    }
                });
            }
        });
    });
}());