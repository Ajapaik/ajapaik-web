var map;

function get_map(startpoint) {
    // Starting point
    if (startpoint == undefined) {
    	var latlng = new google.maps.LatLng(59.437,24.76);
    } else {
        var latlng = new google.maps.LatLng(startpoint[1], startpoint[0]);
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
    	maxZoom: 19
    });
	
	var mapOpts = {
		zoom: 14,
		center: latlng,
        mapTypeId: 'OSM',
        mapTypeControlOptions: {
        	  mapTypeIds: ['OSM', google.maps.MapTypeId.ROADMAP],
        	  style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
        }
		
	};
	
	map = new google.maps.Map(document.getElementById("map_canvas"), mapOpts);
	map.setCenter(latlng);
	map.setZoom(14);
	
	// Attach base layer
	map.mapTypes.set('OSM', osmMapType);
	map.setMapTypeId('OSM');

    return map
}

$(document).ready(function() {

    $('.photo-item').hover(function () {
        $('.original .tools, .rephoto .meta').addClass('hovered');
    },function () {
        $('.original .tools, .rephoto .meta').removeClass('hovered');
    });

});