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
    var fetchComments = function() {
        var _setup_links_in_comments = function() {
            $('#ajapaik-comment-list .comment-text a').attr('target', '_blank');
        };

        var _setup_comment_count = function(count) {
            comments_count = $('#ajapaik-photo-modal-discuss span[class~="badge"]');
            if(comments_count) {
                comments_count.html(count);
                if(count === 0) {
                    comments_count.addClass('hidden');
                }
                else {
                    comments_count.removeClass('hidden');
                }
            }
        };

        $.ajax({
            type: 'GET',
            url: '/comments/for/' + photo_id + '/',
            success: function (response) {
                $('#ajapaik-comment-list').html(response.content);
                $('[data-toggle=confirmation]').confirmation({
                    rootSelector: '[data-toggle=confirmation]',
                });
                _setup_comment_count(response.comments_count);
                _setup_links_in_comments();
            }
        });
    };
    fetchComments();


    var post_comment = function(form) {
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
                fetchComments();
            }
        });
    };


    // Post new commetn (send button pressed).
    $('#ajapaik-comment-form').submit(function(event) {
        var form = $('#ajapaik-comment-form');
        post_comment(form);
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
                    fetchComments();
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
        post_comment(form);
        event.preventDefault();
    });


    // Show edit form (edit link pressed).
    $('#ajapaik-comment-list').on('click', 'a[data-action="edit"]', function(event) {
        var comment_id = $(event.target).data('comment-id');
        var all_edit_form_divs = $('#ajapaik-comment-list div[class*="comment-edit-form-"]');
        var edit_form_div = $('#ajapaik-comment-list div[class~="comment-edit-form-' + comment_id + '"]');
        var comment_container = $('#c' + comment_id + ' .comment-text');
        var comment_text = comment_container.data('comment-text');
        var comment_textarea = edit_form_div.find('textarea');

        comment_textarea.val(comment_text);

        // Hide all forms and show only requested.
        all_edit_form_divs.addClass('hidden');
        comment_container.addClass('hidden');
        edit_form_div.removeClass('hidden');

        event.preventDefault();
    });


    // Exit edit form (cancel button pressed).
    $('#ajapaik-comment-list').on('click', 'button[data-action="cancel"]', function(event) {
        var comment_id = $(event.target).data('comment-id');
        var all_edit_form_divs = $('#ajapaik-comment-list div[class*="comment-edit-form-"]');
        var comment_container = $('#c' + comment_id + ' .comment-text');

        comment_container.removeClass('hidden');
        all_edit_form_divs.addClass('hidden');
    });


    // Update comment (edit button pressed).
    $('#ajapaik-comment-list').on('click', 'button[data-action="edit"]', function(event) {
        var comment_id = $(event.target).data('comment-id');
        var form = $('#ajapaik-comment-list div[class~="comment-edit-form-' + comment_id + '"]').find('form');
        $.ajax({
            type: 'POST',
            url: '/comments/edit-one/',
            data: form.serialize(),
            success: function (response) {
                console.log(response);
                fetchComments();
            }
        });
        event.preventDefault();
    });
});
