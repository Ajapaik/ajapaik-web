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
				'width': '75%',
				'height': '75%',
				'autoScale': false,
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

function uploadCompleted(response) {
	$.modal.close();
	if (typeof photoId == 'undefined') {
		if (typeof response.new_id != 'undefined' && response.new_id) {
			window.location.href = '/foto/'+ response.new_id +'/';
		}
		else {
			window.location.reload();
		}
	}
	else {
		closePhotoDrawer();
		if (typeof response.new_id != 'undefined' && response.new_id) {
			loadPhoto(response.new_id);
		}
		else {
			loadPhoto(photoId);
		}
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
	$('#photo-drawer').delegate('#random-photo', 'click', function(e) {
		e.preventDefault();
		loadPhoto(geotagged_photos[Math.floor(Math.random()*geotagged_photos.length)][0]);
	});

	$('#photo-drawer').delegate('ul.thumbs li.photo a', 'click', function(e) {
		e.preventDefault();
		$('#rephoto_content a').attr('href', rephoto_img_href[$(this).attr('rel')]);
		$('#rephoto_content img').attr('src', rephoto_img_src[$(this).attr('rel')]);
		$('#meta_content').html(rephoto_meta[$(this).attr('rel')]);
		$('#add-comment').html(rephoto_comment[$(this).attr('rel')]);
		if (typeof FB != 'undefined') {
			FB.XFBML.parse();
		}
		History.replaceState(null, window.document.title, $(this).attr('href'));
		_gaq.push(['_trackPageview', $(this).attr('href')]);
	});

	$('#photo-drawer').delegate('a.add-rephoto', 'click', function(e) {
		e.preventDefault();
		$('#notice').modal();
		_gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
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
		'width': '75%',
		'height': '75%',
		'autoScale': false,
		'hideOnContentClick': false
	});


/*
	$('#photo-drawer').delegate('#upload', 'click', function(e) {
		$('#upload_field').trigger('click');
	});
*/

});