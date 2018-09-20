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
                '<div id="ajapaik-photo-modal-map-state"></div>',
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
            var osm = new L.TileLayer(osmUrl, {minZoom: 5, maxZoom: 18, attribution: osmAttrib});

            that.initialMapCenter = {
                lat: that.options.latitude,
                lng: that.options.longitude
            };
// Show map layers
            map.addLayer(osm);
            map.setView(that.initialMapCenter, 16);

            // Draw pointer and markerline if we know direction
            if (that.options.azimuth) {
                var marker = this.getMarkerArrow(that.initialMapCenter, that.options);
                marker.addTo(map);
                that.options.marker=marker;

                var markerline=this.getMarkerLine(that.initialMapCenter, that.options);
                map.addLayer(markerline);
                that.options.markerline=markerline;
            }
            else
            {
                var marker = this.getMarker(that.initialMapCenter);
                marker.addTo(map);
                that.options.marker=marker;
            }

// Topright corner user count
            if (typeof(that.options.geotaggingUserCount) !== "undefined" ) {
               var geotaggingUserCount=this.getGeotaggingUserCountButton(that.options);
               geotaggingUserCount.addTo(map);
            }

            var startGeotaggingButton = this.getStartGeotaggingButton(that.options);
            startGeotaggingButton.addTo(map);
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
               $("i.ajapaik-minimap-start-geotagging").parent().parent().css('width', '4em');
               $("i.ajapaik-minimap-start-geotagging").parent().parent().parent().css('background-color', 'white');
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
        },

        getStartGeotaggingButton : function(options) {
                var e=$("<i>add_location</i>");
		e.css("font-size", "300%");
		e.css("padding-top", "0.1em");
		e.addClass("ajapaik-minimap-start-geotagging");
		e.addClass("material-icons");
                e.addClass('notranslate');

                var html_value=$("<div>").append(e).html();
                options.position='bottomright';
		options.onStartCrosshairGeotagging=this.doStartCrosshairGeotagging;
		options.onStartCameraGeotagging=this.doStartCameraGeotagging;

                var button=L.easyButton(html_value, this.doStartGeotagging, 'geotaggingbutton', options);
                return button;
        },
        getSubmitGeotaggingButton : function(options) {
                var e=$("<i>submit</i>");
		e.css("font-size", "300%");
		e.css("padding-top", "0.1em");
		e.addClass("ajapaik-minimap-start-geotagging");
		e.addClass("material-icons");
                e.addClass('notranslate');

                var html_value=$("<div>").append(e).html();
                options.position='bottomright';

                var button=L.easyButton(html_value, this.doSubmitGeotagging, 'geotaggingbutton', options);
                return button;
        },

        getCancelGeotaggingButton : function(options) {
                var e=$("<i>cancel</i>");
		e.css("font-size", "300%");
		e.css("padding-top", "0.1em");
		e.addClass("ajapaik-minimap-start-geotagging");
		e.addClass("material-icons");
                e.addClass('notranslate');

                var html_value=$("<div>").append(e).html();
                options.position='bottomright';

                var button=L.easyButton(html_value, this.doCancelGeotagging, 'geotaggingbutton', options);
                return button;
        },

	doCancelGeotagging : function (eb_this) {

	},

	doSubmitGeotagging : function (eb_this) {

	},


	doStartCrosshairGeotagging : function(eb_this) {
                var that=eb_this.options.context;
                var map=window.ajapaikminimap;

                if (that.options.mode=='crosshair') return;
	
                const defaults = {
                      crosshairHTML: '<img alt="Center of the map; crosshair location" title="Crosshair" src="/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg" width="38px" />'
                }

                if (that.options.cameramarker) {
			map.setView(that.options.cameramarker.getCameraLatLng());
			that.options.targetLatLng=that.options.cameramarker.getTargetLatLng();
			that.options.cameramarker.remove();
		}
                that.options.mode='crosshair';
                that.options.crosshairmarker=L.geotagPhoto.crosshair(defaults)
                that.options.crosshairmarker.addTo(map)
                    .on('input', function (event) {
//                        var point = getCrosshairPoint()
                    })
        },
        doStartCameraGeotagging : function(eb_this) {
                var that=eb_this.options.context;
                map=window.ajapaikminimap;
                var azimuth = that.options.azimuth ? that.options.azimuth : 0 ;

                if (that.options.mode=='camera') {
	                var northWest = map.getBounds().getNorthWest();
        	        var northEast = map.getBounds().getNorthEast();
                	var southWest = map.getBounds().getSouthWest();
			var dist_nwne=northWest.distanceTo(northEast) / 3;
			var dist_nwsw=northWest.distanceTo(southWest) / 3;
			var dist=(dist_nwne>dist_nwsw ? dist_nwsw : dist_nwne);

			azimuth=L.GeometryUtil.bearing(that.options.cameramarker.getCameraLatLng(),that.options.cameramarker.getTargetLatLng());
	                var destinationPoint= L.GeometryUtil.destination(that.options.cameramarker.getCameraLatLng(), azimuth, dist);
			map.setView(that.options.cameramarker.getCameraLatLng());

			that.options.cameramarker.setTargetLatLng(destinationPoint);
			return;
		}

                that.options.mode='camera';

                var initialMapCenter = {
                   lat: that.options.latitude,
                   lng: that.options.longitude
                };

                if (that.options.crosshairmarker) {
			initialMapCenter=that.options.crosshairmarker.getCrosshairLatLng();
			that.options.crosshairmarker.removeFrom(map);
		}



		var destinationPoint;

		if (that.options.targetLatLng) {
			destinationPoint=that.options.targetLatLng;
		}
		else
		{
	                var center = map.getCenter();
        	        var northWest = map.getBounds().getNorthWest();
                	var northEast = map.getBounds().getNorthEast();
                	var southWest = map.getBounds().getSouthWest();

			var dist_nwne=northWest.distanceTo(northEast) / 3;
			var dist_nwsw=northWest.distanceTo(southWest) / 3;
			var dist=(dist_nwne>dist_nwsw ? dist_nwsw : dist_nwne);

	                destinationPoint= L.GeometryUtil.destination(initialMapCenter, azimuth, dist);
		}
                var cameraPoint = [initialMapCenter.lng, initialMapCenter.lat];
    	        var targetPoint = [destinationPoint.lng, destinationPoint.lat];



                var points = {
                    type: 'Feature',
                    properties: {
                        angle: 20
                    },
                    geometry: {
                        type: 'GeometryCollection',
                        geometries: [
                            {
                                type: 'Point',
                                coordinates: cameraPoint
                            },
                            {
                                type: 'Point',
                                coordinates: targetPoint
                            }
                        ]
                    }
                }
                var options = {
                    cameraIcon: L.icon({
                    iconUrl: '/static/images/camera.svg',
                    iconSize: [38, 38],
                    iconAnchor: [19, 19]
                }),
                targetIcon: L.icon({
                    iconUrl: '/static/images/marker.svg',
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                }),
                angleIcon: L.icon({
                    iconUrl: '/static/images/marker.svg',
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                }),
                control:false,
                angleMarker: false,
                minangle:1,
                controlCameraImg: '/static/images/camera-icon.svg',
                controlCrosshairImg: '/static/images/crosshair-icon.svg',
                };

                var geotagPhotoCamera = L.geotagPhoto.camera(points, options)
                geotagPhotoCamera.addTo(map)
                .on('change', function (event) {
                //    updateSidebar()
                })
                .on('input', function (event) {
                //    updateSidebar()
                })
                geotagPhotoCamera.setAngle(1)
                that.options.cameramarker=geotagPhotoCamera;
                 var fieldOfView = geotagPhotoCamera.getFieldOfView()
//               alert(JSON.stringify(initialMapCenter) + "\n" + JSON.stringify(fieldOfView, null, 2))
 	},

        doStartGeotagging : function() {
//		alert(this.options.marker);
                if (this.options.mode=='map') {
                    this.options.mode='camera';
                    if (this.options.marker) this.options.marker.remove();
                    if (this.options.markerline) this.options.markerline.remove();
                    var map=window.ajapaikminimap;
                    var button_options={
                        position: 'topleft', 
                        controlCameraImg: '/static/images/camera-icon.svg', 
                        controlCrosshairImg: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg',
                        context:this
                    }
                    var tb_temp={};
                    tb_temp.options=button_options;
		    alert("foo");
                    this.options.onStartCrosshairGeotagging(tb_temp);

                    var html_value="<a><img src='"+ button_options.controlCameraImg +"'/></a>";
                    var button=L.easyButton(html_value, this.options.onStartCameraGeotagging, 'camerageotaggingbutton', button_options);
//                    button.on('click', this.doStartCameraGeotagging, this)
                    button.addTo(map)

                    html_value="<a><img height='25px' src='"+ button_options.controlCrosshairImg +"'/></a>";
                    button=L.easyButton(html_value, this.options.onStartCrosshairGeotagging, 'crosshairgeotaggingbutton', button_options);
//                    button.on('click', this.doStartCrosshairGeotagging, this)
                    button.addTo(map)
		    this.remove();

		    button=this.getCancelGeotaggingButton(button_options);
		    button.addTo(map);

		    button=this.getSubmitGeotaggingButton(button_options);
		    button.addTo(map);


		}
	},

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
