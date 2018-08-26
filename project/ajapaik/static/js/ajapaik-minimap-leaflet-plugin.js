(function () {
    'use strict';
    /*global $*/
    /*global L*/

    var AjapaikMinimap = function (node, options) {
        var that = this;
        this.node = node;

        this.options = $.extend({}, options);
        // Do not show map if isMobile is true
        if (options.isMobile) {
            return;
        }
        // Create map only if we have coordinates
        else if (options.latitude && options.longitude)
        {
            this.UI = $([
                '<div id="ajapaik-minimap-disabled-overlay"></div>',
                '<div id="ajapaik-photo-modal-map-canvas"></div>',
                '<div id="ajapaik-photo-modal-map-textbox"></div>',
            ].join('\n'));

            $(this.node).html(this.UI);
            $(this.node).css("z-index", "99");
            $(this.node).show();
            this.initializeMap();
        }
        else
        {
/*            this.buildStartGeotaggingButton = function (photoHasLocation) {
                var button = $([
                    '<button id="ajapaik-minimap-disabled-overlay"></div>',
                    '<div id="ajapaik-photo-modal-map-canvas"></div>'
                ].join('\n'));
            };*/
        }
    };
    AjapaikMinimap.prototype = {
        constructor: AjapaikMinimap,
        initializeMap: function () {
            var that = this;
            if (that.options.isMobile) {
                $(that.node).removeClass('col-xs-3').addClass('col-xs-9');
                that.options.height=250;
            }
            else
            {
                that.options.height=480;
            }
            that.mapCanvas = that.UI.find('#ajapaik-photo-modal-map-canvas');
            $(that.node).css('height', that.options.height + 'px');
            var map = L.map('ajapaik-photo-modal-map-canvas', { fullscreenControl: true });

// OSM layer
            var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	    var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
            var osm = new L.TileLayer(osmUrl, {minZoom: 5, maxZoom: 17, attribution: osmAttrib});

            that.initialMapCenter = {
                lat: that.options.latitude,
                lng: that.options.longitude
            };
// Show map layers
            map.addLayer(osm);
            map.setView(that.initialMapCenter, 14);

            // Draw pointer and markerline if we know direction
            if (that.options.azimuth) {
                var marker = this.getMarkerArrow(that.initialMapCenter, that.options);
                marker.addTo(map);

                var markerline=this.getMarkerLine(that.initialMapCenter, that.options);
                map.addLayer(markerline);
            }
            else
            {
                var marker = this.getMarker(that.initialMapCenter);
                marker.addTo(map);
            }

// Topright corner user count
            if (typeof(that.options.geotaggingUserCount) !== "undefined" ) {
               var geotaggingUserCount=this.getGeotaggingUserCountButton(that.options);
               geotaggingUserCount.addTo(map);
            }
// global reference to map for ajapaik-common-nogooglemaps.js
            window.ajapaikminimap=map;

// add helper text
            var coordinatelink=this.getCoordinateLink(that.initialMapCenter);
            $("#ajapaik-photo-modal-map-textbox").append(coordinatelink);

// In modal view map doesn't know it's size until elements are created
	    setTimeout(function () {
               map.invalidateSize();

               // overwrite L.easybutton look and feel
               $("span.ajapaik-minimap-geotagging-user-text").css('padding-left', '2em');
               $("span.ajapaik-minimap-geotagging-user-text").parent().parent().css('cursor', 'default');
               $("span.ajapaik-minimap-geotagging-user-text").parent().parent().css('pointer-events', 'none');
               $("span.ajapaik-minimap-geotagging-user-text").parent().parent().css('width', '4.5em');
               $("span.ajapaik-minimap-geotagging-user-text").parent().parent().parent().css('background-color', 'white');
            }, 500);

// For slow networks (500 ms failed in train)
	    setTimeout(function () {
               map.invalidateSize();
            }, 1000);

        },
        getCoordinateLink : function(point) {
            var link=$("<a>");
            var url="https://www.openstreetmap.org/?mlat=" + point.lat + "&mlon=" + point.lng +"#map=15/" + point.lat + "/" + point.lng;
            link.attr('href', url);
            link.text(point.lat + "° N " + point.lng + "° E");
            return link;
        },

        getMarkerArrow : function(point, options) {
            // FIXME: svg doesn't work with msie;

            // https://commons.wikimedia.org/wiki/File:Ic_navigation_48px.svg
            var pointerIcon = new L.icon({
                 iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Ic_navigation_48px.svg/200px-Ic_navigation_48px.svg.png',
                 iconSize:     [48, 48], // size of the icon
                 iconAnchor:   [24, 0], // point of the icon which will correspond to marker's location
                 popupAnchor:  [-3, -26] // point from which the popup should open relative to the iconAnchor
            });

            var markerOptions={
                icon: pointerIcon,
                rotationAngle:options.azimuth
            }
            return L.marker(point, markerOptions);
        },

        getMarker : function(point, options) {
            // FIXME: svg doesn't work with msie;

            // https://commons.wikimedia.org/wiki/File:Ic_location_on_48px.svg
            var pointerIcon = new L.icon({
                 iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Ic_location_on_48px.svg/200px-Ic_location_on_48px.svg.png',
                 iconSize:     [48, 48], // size of the icon
                 iconAnchor:   [24, 48], // point of the icon which will correspond to marker's location
                 popupAnchor:  [-3, -26] // point from which the popup should open relative to the iconAnchor
            });
            return L.marker(point, {icon: pointerIcon });
        },

        getMarkerLine : function(startingPoint, options) {
                var destinationPoint= L.GeometryUtil.destination(startingPoint, options.azimuth, 500000);
		var pointList = [startingPoint, destinationPoint];
                var markerline = new L.Polyline(
                                                pointList,
                                                {
                                                    color: 'red',
                                                    weight: 3,
                                                    opacity: 0.5,
                                                    smoothFactor: 1,
                                                    dashArray: '7,7'
                                                });
                return markerline;
        },
        getGeotaggingUserCountButton : function(options) {
                var e=$("<span>");
		e.addClass("ajapaik-minimap-geotagging-user-text");
		e.css("font-size", "150%");
		e.text(options.geotaggingUserCount);

                if (options.geotaggingUserCount == 1 ) e.addClass("ajapaik-minimap-geotagging-user-single-person");
                else if (options.geotaggingUserCount > 1 ) e.addClass("ajapaik-minimap-geotagging-user-multiple-people");
                if (options.userHasGeotaggedThisPhoto==1) e.addClass("ajapaik-minimap-geotagging-user-active")

                // create temporary div to get the outerhtml
                var html_value=$("<div>").append(e).html(); 
                var button=L.easyButton(html_value, function() {});
                button.disable();
                return button;
        }
    };

    // FIXME: Supports only one minimap. 
    $.fn.AjapaikMinimap = function (options) {
        return this.each(function () {
            $(this).data('AjapaikMinimap', new AjapaikMinimap(this, options));
        });
    };
}());

// Helper function for Reading global variables from project/ajapaik/templates/_photo_modal.html

function get_photoviewModalOptions()
{
        var options={};
        if (window.photoModalPhotoLat && window.photoModalPhotoLng)
        {
           options={
                       latitude  : window.photoModalPhotoLat,
                       longitude : window.photoModalPhotoLng,
                       azimuth   : window.photoModalPhotoAzimuth
                   };
        }
        else if (window.photoModalExtraLat && window.photoModalExtraLng)
        {
            options={
                       latitude  : window.photoModalExtraLat,
                       longitude : window.photoModalExtraLng,
                       azimuth   : null
                    };
        }

        options.geotaggingUserCount=0;
        if (window.photoModalGeotaggingUserCount)
        {
                options.geotaggingUserCount=parseInt(window.photoModalGeotaggingUserCount);
        }

        options.userHasGeotaggedThisPhoto=0;
        if (window.photoModalUserHasGeotaggedThisPhoto)
        {
                options.userHasGeotaggedThisPhoto=1;
        }
        options.isMobile=window.isMobile;
        options.title = window.title;
        options.description = window.description;

	return options;
}
