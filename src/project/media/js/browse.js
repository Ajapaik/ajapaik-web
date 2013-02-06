/* FUNCTIONS */

	/* browse */
var photoId;

function loadPhoto(id) {
	photoId = id;
	$.ajax({
		cache: false,
		url: '/foto/'+id+'/',
		success: function(result) {
			openPhotoDrawer(result);
			if (typeof FB != 'undefined') {
				FB.XFBML.parse();
			}
		},
		error: function (result) {
			alert('error');
		}
	});
}

function openPhotoDrawer(content) {
	$('#photo-drawer').html(content);
	$('#photo-drawer').animate({ top : '7%' });
}

function closePhotoDrawer() {
	$('#photo-drawer').animate({ top : '-100%' });
}

function uploadCompleted() {
	$.modal.close();
	if (typeof photoId == 'undefined') {
		window.location.reload();
	}
	else {
		closePhotoDrawer();
		loadPhoto(photoId);
	}
}

/* INIT */

$(document).ready(function() {

/* BINDINGS */

	/* browse */

	$('#open-photo-drawer').click(function(e) {
		e.preventDefault();
		openPhotoDrawer();
	});

	$('#photo-drawer').delegate('#close-photo-drawer', 'click', function(e) {
		e.preventDefault();
		closePhotoDrawer();
	});

	$('#photo-drawer').delegate('ul.thumbs li.photo a', 'click', function(e) {
		e.preventDefault();
		$('#rephoto_img').attr('src', $(this).attr('rel') );
		if ($(this).attr('title')) {
			$('#meta_content').html($(this).attr('title'));
		}
		else {
			$('#meta_content').html('');
		}
	});

	$('#photo-drawer').delegate('a.add-rephoto', 'click', function(e) {
		e.preventDefault();
		$('#notice').modal();
	});
	
    $('#browse #photo-drawer .original, .single .original').hover(function () {
        $('.original .tools').addClass('hovered');
    },function () {
        $('.original .tools').removeClass('hovered');
    });
	$('#browse #photo-drawer .rephoto .container, .single .rephoto .container').hover(function () {
        $('.rephoto .container .meta').addClass('hovered');
    },function () {
        $('.rephoto .container .meta ').removeClass('hovered');
    });


/*
	$('#photo-drawer').delegate('#upload', 'click', function(e) {
		$('#upload_field').trigger('click');
	});
*/

});