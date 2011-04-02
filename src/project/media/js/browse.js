/* FUNCTIONS */

	/* browse */

function openPhotoDrawer(content) {
	$('#photo-drawer').html(content);
	$('#photo-drawer').animate({ top : '7%' });
}

function closePhotoDrawer() {
	$('#photo-drawer').animate({ top : '-100%' });
}

/* INIT */

$(document).ready(function() {

/* BINDINGS */

	/* browse */

	$('#open-photo-drawer').click(function(e) {
		e.preventDefault();
		openPhotoDrawer();
	});

	$('#close-photo-drawer').click(function(e) {
		e.preventDefault();
		closePhotoDrawer();
	});

	$('#photo-drawer').delegate('ul.thumbs li.photo a', 'click', function(e) {
		e.preventDefault();
		$('.rephoto > img').attr('src', $(this).attr('rel') );
	});

	$('#photo-drawer').delegate('ul.thumbs li.add-rephoto a', 'click', function(e) {
		e.preventDefault();
		$('#notice').modal();
	});

/*
	$('#photo-drawer').delegate('#upload', 'click', function(e) {
		$('#upload_field').trigger('click');
	});
*/

});