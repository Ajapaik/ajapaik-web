function HelsinkiGooglemApi(_, isGeotagger) {
    'use strict';
    /*global google*/
    /*global gettext*/
    var that = this;
    var historicalUrl = "https://geoserver.hel.fi/geoserver/historical/wms?";
    var ortoUrl = "https://geoserver.hel.fi/geoserver/hel/wms?";
    this.vars = {
        layers: [
            {year: "1878", name:"historical:1878_asemakaavakartta", url: historicalUrl}, //historical:1878_asemakaavakartta"
            {year: "1900", name:"historical:1900_opaskartta", url: historicalUrl}, //historical:1900_opaskartta
            {year: "1925", name:"historical:1925_opaskartta", url: historicalUrl}, //historical:1925_opaskartta	
            {year: "1940", name:"historical:1940_opaskartta", url: historicalUrl}, //historical:1940_opaskartta
            {year: "1943", name:"hel:orto1943", url: ortoUrl}, //hel:orto1943
            {year: "1962", name:"historical:1962_opaskartta", url: historicalUrl}, //historical:1962_opaskartta
            //{year: "1969", name:"karrta.hel", url: ortoUrl}, //karrta.hel
            {year: "1988", name:"hel:orto1988", url: ortoUrl}, //hel:orto1988
            //{year: "1997", name:"karrta.hel" , url: ortoUrl}, //karrta.hel
            {year: "1999", name:"historical:1999_opaskartta", url: historicalUrl}, //historical:1999_opaskartta
            //{year: "2008", name:"karrta.hel", url: ortoUrl}, //karrta.hel
            //{year: "2016", name:"karrta.hel", url: ortoUrl}, //karrta.hel
            //{year: "2018", name:"karrta.hel", url: ortoUrl} //karrta.hel
        ],
        layerIndex: 1
    };
    this.isGeotagger = isGeotagger;

    this.helsinkiMapType = new google.maps.ImageMapType({
        getTileUrl: function (coord, zoom) {
            var tilesPerGlobe = 1 << zoom,
            x = coord.x % tilesPerGlobe;
            if (x < 0) {
                x = tilesPerGlobe + x;
            }
            return 'https://a.tile.openstreetmap.org/' + zoom + '/' + x + '/' + coord.y + '.png';
          },
        tileSize: new google.maps.Size(256, 256),
        opacity:1.0,
        name: gettext('Old Helsinki'),
        maxZoom: 18
    });

    
    this.setLayer = function(layername, url) {
        let helsinkiHistoricalMapType = new google.maps.ImageMapType({
            getTileUrl: function (coord, zoom) {
                var tilesPerGlobe = 1 << zoom,
                x = coord.x % tilesPerGlobe;
                if (x < 0) {
                    x = tilesPerGlobe + x;
                }
                var s = Math.pow(2, zoom);  
                var twidth = 256;
                var theight = 256;
        
                var gBl = map.getProjection().fromPointToLatLng(
                new google.maps.Point(coord.x * twidth / s, (coord.y + 1) * theight / s)); // bottom left / SW
                var gTr = map.getProjection().fromPointToLatLng(
                new google.maps.Point((coord.x + 1) * twidth / s, coord.y * theight / s)); // top right / NE
        
                // Bounding box coords for tile in WMS pre-1.3 format (x,y)
                var bbox = gBl.lng() + "," + gBl.lat() + "," + gTr.lng() + "," + gTr.lat();
        
                //base WMS URL
                let tileUrl = url;
                tileUrl += "&service=WMS";
                tileUrl += "&version=1.1.0";
                tileUrl += "&request=GetMap";
                tileUrl += "&layers=" + layername;
                tileUrl += "&styles=";
                tileUrl += "&format=image/png";
                tileUrl += "&TRANSPARENT=TRUE";
                tileUrl += "&srs=EPSG:4326";
                tileUrl += "&bbox=" + bbox;
                tileUrl += "&width=256";
                tileUrl += "&height=256";
        
                return tileUrl; 
            },
            tileSize: new google.maps.Size(256, 256),
            opacity: 0.85,
            maxZoom: 18
        });
        map.overlayMapTypes.push(helsinkiHistoricalMapType);
    };
    
    this.changeIndex = function (index) {
        if(index === this.vars.layerIndex || index < 0){
            return;
        }
        this.vars.layerIndex = index;
        map.overlayMapTypes.clear();
        let layer = this.vars.layers[this.vars.layerIndex];
        if(window.map.getMapTypeId() && window.map.getMapTypeId() === 'old-helsinki'){
            this.setLayer(layer.name, layer.url);
        }
        this.refreshMap();
    };
    this.showControls = function () {
        $(that.yearSelection).show();
    };
    this.hideControls = function () {
        $(that.yearSelection).hide();
        map.overlayMapTypes.clear();
    };

    this.buildMapYearControl = function () {
        if (that.yearSelection) {
            that.yearSelection.parentElement.removeChild(that.yearSelection);
        }
        var vanalinnadYearSelection = $('<select class="ajapaik-map-vanalinnad-year-select"></select>');
        $.each(that.vars.layers, function (k, v) {
            var vanalinnadYearSelectionOption = $('<option value="' + k + '">' + v.year + '</option>');
            if (that.vars.layerIndex === k) {
                vanalinnadYearSelectionOption.prop('selected', true);
            }
            vanalinnadYearSelection.append(vanalinnadYearSelectionOption);
        });

        vanalinnadYearSelection.change(function () {
            var value = $(this).val();
            that.changeIndex(value);
            if (typeof window.reportVanalinnadYearChange === 'function') {
                window.reportVanalinnadYearChange(value);
            }
        });

        that.yearSelection = vanalinnadYearSelection.get(0);

        if (that.isGeotagger) {
            vanalinnadYearSelection.css('margin-top', '10px');
            that.yearSelection.index = 2;
            that.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(that.yearSelection);
        } else {
            that.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(that.yearSelection);
        }
    };
    this.refreshMap = function () {
        // Hack to make Google Maps refresh tiles
        var currentZoom = that.map.zoom;
        that.map.setZoom(currentZoom - 1);
        setTimeout(function () {
            that.map.setZoom(currentZoom);
        }, 0);
    };
}