(function ($) {
    'use strict';
    /*global gettext*/
    /*global submitTranscriptionURL*/
    /*global confirmTranscriptionURL*/
    /*global stopTranscriber*/
    /*global docCookies*/
    /*global userIsSocialConnected*/
    var AjapaikTranscriber = function (node, options) {
        var that = this;
        this.node = node;
        this.transcriptionIndex = 0;
        this.options = $.extend({
        }, options);
        this.UI = $([
            "<div id='ajp-transcriber-panel'>",
            "   <div class='card-body'>",
            "       <form class='form' id='ajp-transcriber-form'>",
            "           <textarea class='form-control mb-3' placeholder='' type='text' id='ajp-transcriber-text'></textarea>",
            "           <div id='ajp-transcription-info' class='d-none pb-2' style='justify-content:space-between;'>",
            "               <p id='ajp-transcriber-username'></p>",
            "               <div class='d-flex' style='align-items: flex-end; justify-content: space-evenly; width:200px;'>",
            "                   <button id='ajp-transcriber-previous-button' class='btn btn-outline-primary'>",
            "                       <i class='material-icons notranslate mt-1'>arrow_back</i>",
            "                   </button>",
            "                   <p id='ajp-transcriber-count'></p>",
            "                   <button id='ajp-transcriber-next-button' class='btn btn-outline-primary'>",
            "                       <i class='material-icons notranslate mt-1'>arrow_forward</i>",
            "                   </button>",
            "               </div>",
            "           </div>",
            "           <div id='ajp-transcriber-container-actions' class='d-none'>",
            "               <div class='d-flex'>",
            "                   <button type='submit' id='ajp-transcriber-submit-button' class='btn btn-block btn-success w-50 mr-1 mt-2'></button>",
            "                   <button type='button' id='ajp-transcriber-cancel-button' class='btn btn-block btn-danger w-50 ml-1'></button>",
            "               </div>",
            "               <button type='button' id='ajp-transcriber-confirm-button' class='btn btn-block btn-primary d-none mt-2'></button>",
            "           </div>",
            "           <div class='d-none text-center' id='ajp-transcriber-anonymous-user'>",
            "               <span id='ajp-transcriber-anonymous-user-disclaimer'></span>",
            "               <br>",
            "               <div class='d-flex'>",
            "                   <button id='ajp-transcriber-login' type='button' class='btn btn-block btn-primary w-50 mt-2 mr-1'></button>",
            "                   <button type='button' id='ajp-transcriber-cancel-button2' class='btn btn-block btn-danger w-50 ml-1'></button>",
            "               </div>",
            "           </div>",
            "       </form>",
            "   </div>",
            "</div>"
        ].join('\n'));
        this.submit = function () {
            var payload = {
                    photo: that.photo,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
                    text: that.$UI.find('#ajp-transcriber-text').val()
                };
            $.ajax({
                type: 'POST',
                url: submitTranscriptionURL,
                data: payload,
                success: function (response) {
                    if (typeof window.updateTranscriptions === 'function') {
                        window.updateTranscriptions();
                        if (typeof window.stopTranscriber === 'function') {
                            window.stopTranscriber();
                        }
                    }                    
                    $.notify(response.message, {type: 'success'});
                },
                error: function (response) {
                    $.notify(response.responseJSON.error, {type: 'danger'});
                }
            });
        };
        this.confirmCurrentTranscription = function () {
            if(window.currentPhotoTranscriptions) {
                var payload = {
                        id: window.currentPhotoTranscriptions[0].id,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    };
                $.ajax({
                    type: 'POST',
                    url: confirmTranscriptionURL,
                    data: payload,
                    success: function (response) {                
                        $.notify(response.message, {type: 'success'});
                    },
                    error: function (response) {
                        $.notify(response.responseJSON.error, {type: 'danger'});
                    }
                });
            }
        };
        this.$UI = $(this.node);
        this.$UI.html(this.UI);
        this.initializeTranscriber();
        this.setTranscriptionData = function (id) {
            that.$UI.find('#ajp-transcriber-text').val(window.currentPhotoTranscriptions[id].text);
            that.$UI.find('#ajp-transcriber-count').html((id + 1) + ' / ' + window.currentPhotoTranscriptions.length);
            that.$UI.find('#ajp-transcriber-username').html(gettext('Transcribed by: ') + window.currentPhotoTranscriptions[id].user_name);
        };
        this.checkTranscriptionButtons = function () {
            if(window.currentPhotoTranscriptions && window.currentPhotoTranscriptions.length > 0) {
                if(this.transcriptionIndex == 0) {
                    $('#ajp-transcriber-previous-button').prop('disabled', true);
                } else {
                    $('#ajp-transcriber-previous-button').prop('disabled', false);
                }
                if(window.currentPhotoTranscriptions.length == this.transcriptionIndex + 1) {
                    $('#ajp-transcriber-next-button').prop('disabled', true);
                } else {
                    $('#ajp-transcriber-next-button').prop('disabled', false);
                }
            } else {
                $('#ajp-transcriber-next-button').prop('disabled', true);
                $('#ajp-transcriber-previous-button').prop('disabled', true);
            }
        };
        this.nextTranscription = function () {
            if(window.currentPhotoTranscriptions.length > this.transcriptionIndex + 1) {
                this.transcriptionIndex += 1;
                that.checkTranscriptionButtons()
                this.setTranscriptionData(this.transcriptionIndex);
            }
        };
        this.previousTranscription = function () {
            if(this.transcriptionIndex > 0) {
                this.transcriptionIndex -= 1;
                that.checkTranscriptionButtons();
            }
            this.setTranscriptionData(this.transcriptionIndex);
        };
        this.$UI = $(this.node);
        this.$UI.html(this.UI);
        this.initializeTranscriber();
    };
    AjapaikTranscriber.prototype = {
        constructor: AjapaikTranscriber,
        initializeTranscriber: function () {
            var that = this;
            that.$UI.find('#ajp-transcriber-next-button').click(function (e) {
                e.preventDefault();
                that.nextTranscription();
            });
            that.$UI.find('#ajp-transcriber-previous-button').click(function (e) {
                e.preventDefault();
                that.previousTranscription();
            });
            that.$UI.find('#ajp-transcriber-confirm-button').text(gettext('This transcription is correct')).attr('title', gettext('Confirm')).click(function (e) {
                that.confirmCurrentTranscription();
            });
            that.$UI.find('#ajp-transcriber-cancel-button, #ajp-transcriber-cancel-button2').text(gettext('Cancel')).attr('title', gettext('Cancel')).click(function (e) {
                e.preventDefault();
                if (typeof window.stopTranscriber === 'function') {
                    window.stopTranscriber();
                }
            });
            that.$UI.find('#ajp-transcriber-text').on('focus', function () {
                window.transcriptionFocused = true;
            }).on('blur', function () {
                window.transcriptionFocused = false;
            }).attr('placeholder', gettext('What is written on the image?'));
            that.$UI.find('#ajp-transcriber-submit-button').text(gettext('Submit')).attr('title', gettext('Submit')).click(function (e) {
                e.preventDefault();
                that.submit();
            });
            $('#ajp-transcriber-text').on('input', function() {
                if(window.currentPhotoTranscriptions && window.currentPhotoTranscriptions.length > 0 && $('#ajp-transcriber-text').val() === window.currentPhotoTranscriptions[that.transcriptionIndex].text) {
                    $('#ajp-transcriber-submit-button').prop('disabled', true);
                }
                else if(!window.currentPhotoTranscriptions || window.currentPhotoTranscriptions.length > 0 && $('#ajp-transcriber-text').val() !== window.currentPhotoTranscriptions[that.transcriptionIndex].text) {
                    $('#ajp-transcriber-submit-button').prop('disabled', false);
                }
            });
            that.$UI.find('#ajp-transcriber-anonymous-user-disclaimer').html(gettext('You\'re anonymous, please login to add transcriptions'));
            
            that.$UI.find('#ajp-transcriber-login').text(gettext('Login')).attr('title', gettext('Login')).click(function () {
                window.openPhotoUploadModal();
            });
            if(window.currentPhotoTranscriptions && window.currentPhotoTranscriptions.length > 0 && !$('#ajp-transcriber-confirm-button').is(':visible')) {
                $('#ajp-transcriber-confirm-button').removeClass('d-none');
            };
        },
        initializeTranscriberState: function (state) {
            var that = this,
                loginDiv = that.$UI.find('#ajp-transcriber-anonymous-user');
            this.photo = state.photoId;
            that.$UI.find('#ajp-transcriber-submit-button').show();
            if (userIsSocialConnected) {
                $('#ajp-transcriber-container-actions').removeClass('d-none');
            } else {
                if(window.currentPhotoTranscriptions.length < 1) {
                    $('#ajp-transcriber-text').addClass('d-none');
                }
                loginDiv.removeClass('d-none');
            }
            if(window.currentPhotoTranscriptions && window.currentPhotoTranscriptions.length > 0) {
                that.setTranscriptionData(that.transcriptionIndex);
                $('#ajp-transcriber-submit-button').prop('disabled', true);
            } else {
                $('#ajp-transcriber-submit-button').prop('disabled', false);
            }
            that.checkTranscriptionButtons();
        }
    };
    $.fn.AjapaikTranscriber = function (options) {
        return this.each(function () {
            $(this).data('AjapaikTranscriber', new AjapaikTranscriber(this, options));
        });
    };
}(jQuery));