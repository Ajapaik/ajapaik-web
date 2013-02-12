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
    map = get_map(start_location, 15);
    
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
        icon: '/media/gfx/icon_marker.png'
    });

	google.maps.event.addListener(map, 'click', function(event){
		if (infowindow !== undefined) {
			infowindow.close();
			infowindow = undefined;
		}
		marker.setPosition(event.latLng);
	});

	google.maps.event.addListener(marker, 'position_changed', function() {
		disableSave = false;
	});

    infowindow = new google.maps.InfoWindow({
        content: gettext('Drag the camera where the picture was taken.')
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
			alert(gettext('Drag the camera where the picture was taken.'));
		}
		else {
			saveLocation();
		}
	});

	$('#photos').delegate('.show-description', 'click', function(e) {
		e.preventDefault();
		hintUsed = 1;
		showDescription();
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
					'<div class="container"><a href="#" class="id'+photos[currentPhotoIdx].id+' btn small show-description">'+gettext('Show hint')+'</a><div class="description">'+photos[currentPhotoIdx].description+'</div><img src="'+mediaUrl+photos[currentPhotoIdx].big.url+'" /></div>'
				).find('img').load(function() {

					currentPhoto.css({ 'visibility' : 'visible' });

					$(this).fadeIn('slow', function() {

						gameWidth += $(currentPhoto).width();
						$('#photos').width(gameWidth);
						scrollPhotos();

					});

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