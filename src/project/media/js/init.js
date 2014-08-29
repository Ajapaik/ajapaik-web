var map;

function get_map(startpoint, startingzoom, isGameMap) {
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
    if (isGameMap) {
        $('<div/>').addClass('center-marker').appendTo(map.getDiv()).click(function () {
            var that = $(this);
            if (!that.data('win')) {
                that.data('win').bindTo('position', map, 'center');
            }
            that.data('win').open(map);
        });
    }

	// Attach base layer
	map.mapTypes.set('OSM', osmMapType);
	map.setMapTypeId('OSM');

	return map;
}

function prepareFullscreen()
{
	$('.full-box img').load(function() {
		var aspectRatio = $(this).width() / $(this).height();
		var new_width = parseInt(screen.height * aspectRatio);
		var new_height = parseInt(screen.width / aspectRatio);
		if (new_width > screen.width)
		{
			new_width = screen.width;
		}
		else {
			new_height = screen.height;
		}
		$(this).css('margin-left', (screen.width-new_width) / 2 +'px');
		$(this).css('margin-top', (screen.height-new_height) / 2 +'px');
		$(this).css('width', new_width);
		$(this).css('height', new_height);
		$(this).css('opacity', 1);
	});
}

$(document).ready(function() {

	$.jQee('esc', function(e) {
		$('#close-photo-drawer').click();
		$('#close-location-tools').click();
	});
	$.jQee('shift+r', function(e) {
		$('#random-photo').click();
	});
    
    $('.filter-box select').change(function(){
        var uri = URI(location.href),
            new_q = URI.parseQuery($(this).val()),
            is_filter_empty = false;
                    
        uri.removeQuery(Object.keys(new_q));
        $.each(new_q, function(i,ii){ is_filter_empty = ii == "" });
                
        if (!is_filter_empty) {
            uri = uri.addQuery(new_q);
        }
        location.href = uri.toString();
    });    

});
