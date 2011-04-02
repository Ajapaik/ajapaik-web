var photos = [];

var gameOffset = 0;
var gameWidth = 0;

var currentPhotoIdx = 0;
var currentPhoto;

var hintUsed = 0;

var mediaUrl = 'http://www.ajapaik.ee/';

/* var streamUrl = 'http://localhost:8001/ajapaik/stream.php'; */
var streamUrl = '/stream';

var disableNext = false;
var locationToolsOpen = false;

function update_leaderboard() {
   $('#scoreboard').load(leaderboardUpdateURL);
}

/* INIT */

$(document).ready(function() {
    update_leaderboard();
    
	loadPhotos();

    // Will load the base map layer and return it
    map = get_map();
    
    // Create marker
    function toggleBounce() {
        if (marker.getAnimation() != null) {
            marker.setAnimation(null);
        } else {
            marker.setAnimation(google.maps.Animation.BOUNCE);
        }
    }
    
    var tallinn = new google.maps.LatLng(59.435474, 24.750309);
    var marker = new google.maps.Marker({
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP,
        position: tallinn,
        icon: 'http://www.ajapaik.ee/media/images/icon_marker.png'
    });


    infowindow = new google.maps.InfoWindow({
        content: 'Sikuta mind sinna kust pilt on tehtud.'
    });

/* BINDINGS */

	/* game */

	$('.skip-photo').click(function(e) {
		e.preventDefault();
		nextPhoto();
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
		saveLocation();
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

	$('#score-container').mouseleave(function() {
		hideScoreboard();
	});

	$('#score-container').mouseenter(function() {
		showScoreboard();
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
			$("#scoreboard li.you score").text(resp['total_score']);

			message = '';
			if (resp['is_correct'] == 'true') {
				message = 'Tundub õige!';
			}
			else
			if (resp['is_location_unknown']) {
				message = 'Siin ei ole täpne koht veel kindlaks tehtud.';		
			}
			else
			if (resp['is_correct'] == 'false') {
				message = 'Aga julgeme kahelda.';		
			}
			else {
				message = 'Sinu pakkumine oli esimene.';
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
		$('#scoreboard li').not('.you').add('h2').slideDown();
		$('#facebook-connect').slideDown();
	}

	function hideScoreboard() {
		$('#scoreboard li').not('.you').add('h2').slideUp();
		$('#facebook-connect').slideUp();
	}

	function showDescription() {
		$(currentPhoto).find('.show-description').fadeOut(function() {
			$(this).parent().find('.description').fadeIn();
		});
	}

	function nextPhoto() {
    	update_leaderboard();
		hintUsed = 0;

		if (photos.length == currentPhotoIdx+1) {
			loadPhotos();
		}

		if (photos.length > currentPhotoIdx) {

			if (disableNext == false) {

				disableNext = true;

				$(currentPhoto).find('img').animate({ 'opacity' : .4 });
				showDescription();

				$('#photos').append(
					'<div class="photo photo'+currentPhotoIdx+'"></div>'
				);

				currentPhoto = $('#photos .photo'+currentPhotoIdx);

				$(currentPhoto).append(
					'<div class="container"><a href="#" class="id'+photos[currentPhotoIdx].id+' btn small show-description">Näita vihjet</a><div class="description">'+photos[currentPhotoIdx].description+'</div><img src="'+mediaUrl+photos[currentPhotoIdx].big.url+'" /></div>'
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
			console.log('End of an array: '+currentPhotoIdx+' >= '+photos.length);
			loadPhotos();
		}

	}

	function scrollPhotos() {
		gameOffset = ($(document).width() / 2) + ($(currentPhoto).width() / 2) - gameWidth;
		$('#photos').animate({ left : gameOffset }, 1000, function(){
			disableNext = false;
		});
	}

	function loadPhotos() {

		$.getJSON(streamUrl, function(data) {

			$.merge(photos, data);

console.log(photos);

			if (currentPhotoIdx <= 0) {
				nextPhoto();
			}

		});

	}

});