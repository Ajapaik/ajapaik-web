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

/* FUNCTIONS */

	/* browse */

	function openPhotoDrawer() {
		$('#photo-drawer').animate({ top : '7%' });
	}

	function closePhotoDrawer() {
		$('#photo-drawer').animate({ top : '-100%' });
	}

});