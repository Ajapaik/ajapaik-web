var photos = [];

var gameOffset = 0;
var gameWidth = 0;

var currentPhotoIdx = 0;
var currentPhoto;

var hintUsed = 0;

var mediaUrl = '';

var streamUrl = '/stream/';

var disableNext = false;
var disableSave = true;
var locationToolsOpen = false;

function update_leaderboard() {
   $('#top .score_container .scoreboard').load(leaderboardUpdateURL);
}

/* INIT */

$(document).ready(function() {
    update_leaderboard();
    
	loadPhotos();
    
    var location = new google.maps.LatLng(start_location[1], start_location[0]);
    
    // Will load the base map layer and return it
	if (city_id) {
		map = get_map(start_location, 15);
	}
	else {
		map = get_map();
	}
    
    // Create marker
    function toggleBounce() {
        if (marker.getAnimation() != null) {
            marker.setAnimation(null);
        } else {
            marker.setAnimation(google.maps.Animation.BOUNCE);
        }
    }
    
    var marker = new google.maps.Marker({
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP,
        position: location,
        icon: '/media/gfx/ajapaik_marker_45px.png'
    });

	google.maps.event.addListener(map, 'click', function(event){
		if (infowindow !== undefined) {
			infowindow.close();
			infowindow = undefined;
		}
		// change position only if marker is idle
		if (marker.getAnimation() != null) {
			marker.setAnimation(null);
		} else {
			marker.setAnimation(google.maps.Animation.BOUNCE);
			marker.setPosition(event.latLng);
		}
	});

	google.maps.event.addListener(marker, 'position_changed', function() {
		disableSave = false;
	});

    infowindow = new google.maps.InfoWindow({
        content: gettext('Point the marker to where the picture was taken from.')
    });

/* BINDINGS */

	/* game */

	$('.skip-photo').click(function(e) {
		e.preventDefault();

		var data = {
			photo_id: photos[currentPhotoIdx-1].id,
		};
		$.post(saveLocationURL, data, function () {
			nextPhoto();
		});
		_gaq.push(['_trackEvent', 'Game', 'Skip photo']);

	});

	$('#open-location-tools').click(function(e) {
		e.preventDefault();
		openLocationTools();
	});

	$('#close-location-tools').click(function(e) {
		e.preventDefault();
		closeLocationTools();
	});

	$('#continue-game').click(function(e) {
		e.preventDefault();
		continueGame();
	});

	$('#save-location').click(function(e) {
		e.preventDefault();
		if (disableSave) {
			_gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
			alert(gettext('Point the marker to where the picture was taken from.'));
		}
		else {
			saveLocation();
			_gaq.push(['_trackEvent', 'Game', 'Save location']);
		}
	});

	$('#photos').delegate('.show-description', 'click', function(e) {
		e.preventDefault();
		hintUsed = 1;
		showDescription();
		_gaq.push(['_trackEvent', 'Game', 'Show description']);
	});

	$('#photos a.fullscreen').live('click', function(e) {
		e.preventDefault();
		if (BigScreen.enabled) {
			BigScreen.request($('#game-full'+this.rel)[0]);
		}
	});

	$('.full-box div').live('click', function(e) {
		if (BigScreen.enabled) {
			e.preventDefault();
			BigScreen.exit();
		}
	});

	$('#tools').mouseleave(function() {
		if (locationToolsOpen == true) {
			showPhotos();
		}
	});

	$('#tools').mouseenter(function() {
		if (locationToolsOpen == true) {
			hidePhotos();
		}
	});

	$('#top .score_container').mouseleave(function() {
		hideScoreboard();
	});

	$('#top .score_container').mouseenter(function() {
		showScoreboard();
	});
	
	$('#full_leaderboard').bind('click', function(e) {
		e.preventDefault();
		$('#leaderboard_browser .scoreboard').load(leaderboardFullURL, function() {
		  $('#leaderboard_browser').modal();
		});
		_gaq.push(['_trackEvent', 'Game', 'Full leaderboard']);
	});



/* FUNCTIONS */

	/* game */

	function saveLocation() {

		lat = marker.getPosition().lat();
		lon = marker.getPosition().lng();

		var data = {
			photo_id: photos[currentPhotoIdx-1].id,
			hint_used: hintUsed
		};

		if (lat && lon) {
			data['lat'] = lat;
			data['lon'] = lon;
		}

		$.post(saveLocationURL, data, function(resp) {
			//$("#top .score_container .scoreboard li.you score").text(resp['total_score']);
			update_leaderboard();

			message = '';
			if (resp['is_correct'] == true) {
				message = gettext('Looks right!');
			}
			else
			if (resp['location_is_unclear']) {
				message = gettext('Correct location is not certain yet.');
			}
			else
			if (resp['is_correct'] == false) {
				message = gettext('We doubt about it.');
			}
			else {
				message = gettext('Your guess was first.');
			}
			$("#notice .message").text(message);
			$("#notice").modal();

		}, 'json');

	}

	function openLocationTools() {
		disableNext = true;
		
		$('#tools').animate({ left : '15%' }, function() {
			locationToolsOpen = true;
			var photosLeft = gameOffset - ($(document).width() / 2) + ($(currentPhoto).width() / 2);
			$('#photos').animate({ left : photosLeft+'px' });
			$('#open-location-tools').fadeOut();

			if (infowindow !== undefined) {
				infowindow.open(map,marker);
				google.maps.event.addListener(marker, 'click', toggleBounce);
				google.maps.event.addListener(marker, 'dragstart', function(){
					if (infowindow !== undefined) {
						infowindow.close();
						infowindow = undefined;
					}
				});
			}
		});
	}

	function continueGame() {
		$.modal.close();
		closeLocationTools(1);
	}

	function closeLocationTools(next) {
		locationToolsOpen = false;
		$('#photos').animate({ left : gameOffset });
		$('#tools').animate({ left : '100%' }, function() {
			disableNext = false;
			$('#open-location-tools').fadeIn();
			if (next == 1) {
				nextPhoto();
			}
		});
	}

	function showPhotos() {
		photoWidthPercent = Math.round( ($(currentPhoto).width()) / ($(document).width()) * 100 );
		$('#tools').animate({ left : photoWidthPercent+'%' });
	}

	function hidePhotos() {
		$('#tools').animate({ left : '15%' });
	}

	function showScoreboard() {
		$('#top .score_container .scoreboard li').not('.you').add('h2').slideDown();
		$('#top .score_container #facebook-connect').slideDown();
	}

	function hideScoreboard() {
		$('#top .score_container .scoreboard li').not('.you').add('h2').slideUp();
		$('#top .score_container #facebook-connect').slideUp();
	}

	function showDescription() {
		$(currentPhoto).find('.show-description').fadeOut(function() {
			$(this).parent().find('.description').fadeIn();
		});
	}

	function nextPhoto() {
		//update_leaderboard();
		hintUsed = 0;
		disableSave = true;

/*
		if (photos.length == currentPhotoIdx) {
			loadPhotos();
		}
*/
		if (photos.length > currentPhotoIdx) {

			if (disableNext == false) {

				disableNext = true;

				$('.skip-photo').animate({ 'opacity' : .4 });
				$(currentPhoto).find('img').animate({ 'opacity' : .4 });
				showDescription();

				$('#photos').append(
					'<div class="photo photo'+currentPhotoIdx+'"></div>'
				);

				currentPhoto = $('#photos .photo'+currentPhotoIdx);

				$(currentPhoto).append(
					'<div class="container">'+ (language_code == 'et' ? '<a href="#" class="id'+photos[currentPhotoIdx].id+' btn small show-description">'+gettext('Show hint')+'</a>':'') +'<div class="description">'+photos[currentPhotoIdx].description+'</div><a class="fullscreen" rel="'+photos[currentPhotoIdx].id+'"><img src="'+mediaUrl+photos[currentPhotoIdx].big.url+'" /></a></div>'
				).find('img').load(function() {

					currentPhoto.css({ 'visibility' : 'visible' });

					$(this).fadeIn('slow', function() {

						gameWidth += $(currentPhoto).width();
						$('#photos').width(gameWidth);
						scrollPhotos();

					});

				});
				$('#full-photos').append('<div class="full-box" style="opacity: 0;width: 0px;height: 0px;overflow: hidden;"><div class="full-pic" id="game-full'+photos[currentPhotoIdx].id+'"><img src="'+mediaUrl+photos[currentPhotoIdx].large.url+'" border="0" /></div>');
				
				$('.full-box img').load(function() {
					$(this).css('margin-top', '-'+ $(this).height() / 2 +'px');
					$(this).css('margin-left', '-'+ $(this).width() / 2 +'px');
					$(this).css('opacity', 1);
				});

				currentPhotoIdx++;
			}

		}
		else {
/* 			console.log('End of an array: '+currentPhotoIdx+' >= '+photos.length); */
			loadPhotos(1);
		}

	}

	function scrollPhotos() {
		gameOffset = ($(document).width() / 2) + ($(currentPhoto).width() / 2) - gameWidth;
		$('#photos').animate({ left : gameOffset }, 1000, function(){
			disableNext = false;
			$('.skip-photo').animate({ 'opacity' : 1 });
		});
	}

	function loadPhotos(next) {

		date = new Date(); // IE jaoks oli vajalik erinev URL, seega anname sekundid kaasa

		$.getJSON(streamUrl, {
		  'b': date.getTime(),
		  'city': city_id
        }, function(data) {
			$.merge(photos, data);

/*
console.log('loadPhotos();');
for(var i in photos)
{
	console.log(photos[i].id+' -- '+photos[i].description);
}
*/


			if (next || currentPhotoIdx <= 0) {
				nextPhoto();
			}

		});

	}

});