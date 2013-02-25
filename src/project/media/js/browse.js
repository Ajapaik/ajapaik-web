/* FUNCTIONS */

	/* browse */
var photoId;
var cityId;

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
			$("a.iframe").fancybox({
				'hideOnContentClick': false
			});
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
	History.replaceState(null, null, "/kaart/?city="+cityId);
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
		$('#rephoto_content').html($('#rephoto_img_'+$(this).attr('rel')).html());
		$('#add-comment').html($('#rephoto_comment_'+$(this).attr('rel')).html());
		$('#meta_content').html($('#rephoto_meta_'+$(this).attr('rel')).html());
		History.replaceState(null, null, $(this).attr('href'));
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
	
	$("a.iframe").fancybox({
		'hideOnContentClick': false
	});


/*
	$('#photo-drawer').delegate('#upload', 'click', function(e) {
		$('#upload_field').trigger('click');
	});
*/

});