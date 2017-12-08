$(document).ready(function () {
    var photo_id = window.photoModalCurrentlyOpenPhotoId; //  Just to make name shorter.


    // Set focus for comment form when comment icon pressed.
    $('#ajapaik-photo-modal-discuss').click(function(event){
        event.preventDefault();
        $('#id_comment').focus();
    });

    // Disable hotkeys when typing message.
    $('#ajapaik-comments-container').on('focus', 'textarea', function() {
        window.hotkeysActive = false;
    });
    $('#ajapaik-comments-container').on('blur', 'textarea', function() {
        window.hotkeysActive = true;
    });

    // Ferching comment list when page is loaded and when new comment posted.
    window.fetchComments = function() {
        $.ajax({
            type: 'GET',
            url: '/comments/for/' + photo_id + '/',
            success: function (response) {
                $('#ajapaik-comment-list').html(response.content);
                $('[data-toggle=confirmation]').confirmation({
                    rootSelector: '[data-toggle=confirmation]',
                });
                comments_count = $(
                    '#ajapaik-photo-modal-discuss span[class~="badge"]'
                );
                if(comments_count) {
                    comments_count.html(response.comment_count);
                    if(response.comment_count === 0) {
                        comments_count.addClass('hidden');
                    }
                    else {
                        comments_count.removeClass('hidden');
                    }
                }
            }
        });
    };
    window.fetchComments();


    window.post_comment = function(form) {
        $.ajax({
            type: 'POST',
            url: '/comments/post-one/' + photo_id + '/',
            data: form.serialize(),
            success: function(responce) {
                var error_div = form.find("div[data-comment-element='errors']");
                var comment_textarea = form.find('textarea[name="comment"]');

                if(responce && responce.comment && responce.comment.length){
                    error_div.html(responce.comment[0]);
                    error_div.removeClass('hidden');
                }
                else {
                    error_div.addClass('hidden');
                    comment_textarea.val('');
                }
                window.fetchComments();
            }
        });
    };
    // Post new commetn (send button pressed).
    $('#ajapaik-comment-form').submit(function(event) {
        var form = $('#ajapaik-comment-form');
        window.post_comment(form);
        event.preventDefault();
    });

    // Delete comment (delete link perssed).
    $("#ajapaik-comment-list").on('click', 'h6[class="media-heading"]', function(event) {
        var action = $(event.target).data('action');
        var comment_id = $(event.target).data('comment-id');
        if(action === 'delete' && comment_id) {
            $.ajax({
                type: 'POST',
                url: '/comments/delete-one/',
                data: {
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
                    comment_id: comment_id
                },
                success: function(responce) {
                    window.fetchComments();
                }
            });
            event.preventDefault();
        }
    });

    // Show reply form (reply link pressed).
    $('#ajapaik-comment-list').on('click', 'a[data-action="reply"]', function(event) {
        var comment_id = $(event.target).data('comment-id');
        var all_reply_form_divs = $('#ajapaik-comment-list div[class*="comment-reply-form-"]');
        var reply_form_div = $('#ajapaik-comment-list div[class~="comment-reply-form-' + comment_id + '"]');

        // Hide all forms and show only requested.
        all_reply_form_divs.addClass('hidden');
        reply_form_div.removeClass('hidden');

        event.preventDefault();
    });

    // Exit reply form (cancel button pressed).
    $('#ajapaik-comment-list').on('click', 'button[data-action="cancel"]', function(event) {
        var all_reply_form_divs = $('#ajapaik-comment-list div[class*="comment-reply-form-"]');
        all_reply_form_divs.addClass('hidden');
    });

    // Post reply for comment (reply button pressed).
    $('#ajapaik-comment-list').on('click', 'button[data-action="reply"]', function(event) {
        var comment_id = $(event.target).data('comment-id');
        var form = $('#ajapaik-comment-list div[class~="comment-reply-form-' + comment_id + '"]').find('form');
        window.post_comment(form);
        event.preventDefault();
    });
});