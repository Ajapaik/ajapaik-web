(function () {
    'use strict';
    /* global Hammer */
    /* global gettext */
    /* global confirm */
    /* global toggleRephotoOpenURL */
    /* global docCookies */
    $(document).ready(function () {
        var originalHammertime = new Hammer(document.getElementById('tan-detail-image'), {}),
            rephotoHammertime,
            originalNextButton = $('#tan-detail-next-button'),
            originalPreviousButton = $('#tan-detail-prev-button'),
            rephotoNextButton = $('#tan-detail-rephoto-next-button'),
            rephotoPreviousButton = $('#tan-detail-rephoto-prev-button'),
            rephoto = $('#tan-detail-rephoto-container').find('img');
        if (rephoto.length > 0) {
            rephotoHammertime = new Hammer(rephoto.get(0), {});
            rephotoHammertime.on('swipe', function (ev) {
                if (ev.direction === 2) {
                    if (rephotoNextButton.length > 0) {
                        window.location = rephotoNextButton.prop('href');
                    }
                } else if (ev.direction === 4) {
                    if (rephotoPreviousButton.length > 0) {
                        window.location = rephotoPreviousButton.prop('href');
                    }
                }
            });
        }
        originalHammertime.on('swipe', function (ev) {
            if (ev.direction === 2) {
                if (originalNextButton.length > 0) {
                    window.location = originalNextButton.prop('href');
                }
            } else if (ev.direction === 4) {
                if (originalPreviousButton.length > 0) {
                    window.location = originalPreviousButton.prop('href');
                }
            }
        });
        $('.glyphicon-camera').click(function () {
            $('#camera-file-capture').click();
        });
        $('.glyphicon-ok').click(function () {
            $('form').submit();
        });
        $('#tan-detail-rephoto-delete-button').click(function (e) {
            if (!confirm(gettext('Are you sure?'))) {
                e.preventDefault();
            }
        });
        $('#tan-detail-add-rephoto-to-ajapaik-button').click(function () {
            if (window.rephotoToAjapaikURL) {
                var errorDiv = $('#tan-detail-add-rephoto-error-message'),
                    successDiv = $('#tan-detail-add-rephoto-success-message');
                $.ajax({
                    url: window.rephotoToAjapaikURL,
                    success: function (resp) {
                        if (resp.error) {
                            errorDiv.html(resp.message).show();
                            successDiv.hide();
                        } else {
                            successDiv.html(resp.message).show();
                            errorDiv.hide();
                            $('#tan-detail-add-rephoto-to-ajapaik-button').hide();
                        }
                    },
                    error: function () {
                        errorDiv.html(gettext('Sending failed')).show();
                        successDiv.hide();
                    }
                });
            }
        });
        $('#tan-detail-show-rephoto-checkbox').change(function () {
            var $this = $(this),
                open = $this.is(':checked');
            if (open) {
                open = 1;
            } else {
                open = 0;
            }
            $.ajax({
                method: 'post',
                url: toggleRephotoOpenURL,
                data: {
                    open: open,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    if (response.open) {
                        $this.prop('checked', true);
                    } else {
                        $this.prop('checked', false);
                    }
                }
            });
        });
    });
}());


var form = document.getElementById('file-form');

function previewImage() {
    "use strict";
    var fr = new FileReader();
    fr.readAsDataURL(document.getElementById("camera-file-capture").files[0]);
    $('.glyphicon-ok').show();
    $('#uploadPreview').show();
    fr.onload = function (oFREvent) {
        document.getElementById("uploadPreview").src = oFREvent.target.result;
    };
}