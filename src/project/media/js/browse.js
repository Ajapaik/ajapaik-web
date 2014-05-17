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
	$('#photo-drawer').animate({ top : '-1000px' });
	History.replaceState(null, null, "/kaart/?city__pk="+cityId);
	$('.filter-box').show();
}

function uploadCompleted(response) {
	$.modal.close();
	if (typeof photoId == 'undefined') {
		if (response && typeof response.new_id != 'undefined' && response.new_id) {
			window.location.href = '/foto/'+ response.new_id +'/';
		}
		else {
			window.location.reload();
		}
	}
	else {
		closePhotoDrawer();
		if (response && typeof response.new_id != 'undefined' && response.new_id) {
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
	$('.top .score_container').hoverIntent(showScoreboard, hideScoreboard);

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
		$('ul.thumbs li.photo').removeClass('current');
		$(this).parent().addClass('current');
		$('#rephoto_content a').attr('href', rephoto_img_href[$(this).attr('rel')]);
		$('#rephoto_content a').attr('rel', $(this).attr('rel'));
		$('#rephoto_content img').attr('src', rephoto_img_src[$(this).attr('rel')]);
		$('#full-large2 img').attr('src', rephoto_img_src_fs[$(this).attr('rel')]);
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

	$('.single .original').hoverIntent(function () {
		$('.original .tools').addClass('hovered');
	},function () {
		$('.original .tools').removeClass('hovered');
	});
	$('.single .rephoto .container').hoverIntent(function () {
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
	
	$('.full-box div').live('click', function(e) {
		if (BigScreen.enabled) {
			e.preventDefault();
			BigScreen.exit();
		}
	});

	$('#full-thumb1').live('click', function(e) {
		if (BigScreen.enabled) {
			e.preventDefault();
			BigScreen.request($('#full-large1')[0]);
			_gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-'+this.rel]);
		}
	});
	$('#full-thumb2').live('click', function(e) {
		if (BigScreen.enabled) {
			e.preventDefault();
			BigScreen.request($('#full-large2')[0]);
			_gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'rephoto-'+this.rel]);
		}
	});

/*
	$('#photo-drawer').delegate('#upload', 'click', function(e) {
		$('#upload_field').trigger('click');
	});
*/

	$('#full_leaderboard').live('click', function(e) {
		e.preventDefault();
		$('#leaderboard_browser .scoreboard').load(leaderboardFullURL, function() {
		  $('#leaderboard_browser').modal();
		});
		_gaq.push(['_trackEvent', 'Map', 'Full leaderboard']);
	});

	function showScoreboard() {
		$('.top .score_container .scoreboard li').not('.you').add('h2').slideDown();
		$('.top .score_container #facebook-connect').slideDown();
	}

	function hideScoreboard() {
		$('.top .score_container .scoreboard li').not('.you').add('h2').slideUp();
		$('.top .score_container #facebook-connect').slideUp();
	}

});