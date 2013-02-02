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
	
	var mapOpts = {
		zoom: zoom_level,
		center: latlng,
        mapTypeId: 'OSM',
        mapTypeControlOptions: {
        	  mapTypeIds: ['OSM', google.maps.MapTypeId.ROADMAP],
        	  style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
        }
		
	};
	
	map = new google.maps.Map(document.getElementById("map_canvas"), mapOpts);

	// Attach base layer
	map.mapTypes.set('OSM', osmMapType);
	map.setMapTypeId('OSM');

    return map
}