var map;

function get_map(startpoint, startingzoom) {
	// Starting point
	if (startpoint == undefined) {
		var latlng = new google.maps.LatLng(59,26);
		startingzoom = 8;
	} else {
		var latlng = new google.maps.LatLng(startpoint[1], startpoint[0]);
	}
	// Starting point
	if (typeof startingzoom == 'undefined') {
		var zoom_level = 13;
	} else {
		var zoom_level = startingzoom;
	}
	
	// New base layer
	var osmMapType = new google.maps.ImageMapType({
		getTileUrl: function(coord, zoom) {
			return "http://tile.openstreetmap.org/" +
			zoom + "/" + coord.x + "/" + coord.y + ".png";
		},
		tileSize: new google.maps.Size(256, 256),
		isPng: true,
		alt: "OpenStreetMap layer",
		name: "OSM",
		maxZoom: 18
	});
	
	var streetViewOptions = {
		panControl: true,
		panControlOptions: {
		  position: google.maps.ControlPosition.LEFT_CENTER
		},
		zoomControl: true,
		zoomControlOptions: {
			position: google.maps.ControlPosition.LEFT_CENTER
		},
		addressControl: false,
		linksControl: true,
		linksControlOptions: {
			position: google.maps.ControlPosition.BOTTOM_CENTER
		},
		enableCloseButton: true,
		visible: false
	};
	var street = new google.maps.StreetViewPanorama(document.getElementById('map_canvas'), streetViewOptions);

	var mapOpts = {
		zoom: zoom_level,
		center: latlng,
		mapTypeControl: true,
		mapTypeControlOptions: {
			mapTypeIds: ['OSM', google.maps.MapTypeId.ROADMAP],
			style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
		},
		panControl: true,
		panControlOptions: {
			position: google.maps.ControlPosition.LEFT_CENTER
		},
		zoomControl: true,
		zoomControlOptions: {
			position: google.maps.ControlPosition.LEFT_CENTER
		},
		streetViewControl: true,
		streetViewControlOptions: {
			position: google.maps.ControlPosition.LEFT_CENTER
		},
		streetView: street
	};
	map = new google.maps.Map(document.getElementById("map_canvas"), mapOpts);

	// Attach base layer
	map.mapTypes.set('OSM', osmMapType);
	map.setMapTypeId('OSM');

	return map
}

// Stuff which is included in EVERY view. PERIOD! (MANOWAR rules)
$(document).ready(function() {
    
    // Hotkeys
    $.jQee('esc', function(e) {
        $('#close-photo-drawer').click();
        $('#close-location-tools').click();
    });
    $.jQee('space', function(e) {
        $('#open-location-tools').click();
    });
    $.jQee('enter', function(e) {
        $('#save-location').click();
    });
    $.jQee('right', function(e) {
        $('#skip-photo').click();
    });

});