function VanalinnadGooglemApi() {
    'use strict';
    /*global google*/
    var that = this;
    this.empty = {};
    this.vars = {
        layers: [],
        layerIndex: -1,
        site: 'Tallinn',
        vanalinnadPrefix: '/vanalinnad.mooo.com/',
        vanalinnadTiles: '/vanalinnad.mooo.com/'
    };
    this.vanalinnadCitiesMap = {
        'Haapsalu': 'Haapsalu',
        'Kuressaare': 'Kuressaare',
        'Narva': 'Narva',
        'Paide': 'Paide',
        'Pärnu': 'Parnu',
        'Rakvere': 'Rakevere',
        'Tallinn': 'Tallinn',
        'Tartu': 'Tartu',
        'Valga': 'Valga',
        'Viljandi': 'Viljandi',
        'Võru': 'Voru'
    };
    this.juksMapType = new google.maps.ImageMapType({
        getTileUrl: function (coord, zoom) {
            // 'Wrap' x (longitude) at 180th meridian properly
            // NB: Don't touch coord.x because coord param is by reference, and changing it's x property breaks something in Google's lib
            var tilesPerGlobe = 1 << zoom,
                x = coord.x % tilesPerGlobe;
            if (x < 0) {
                x = tilesPerGlobe + x;
            }
            // Wrap y (latitude) in a like manner if you want to enable vertical infinite scroll
            var tmsY = ((1 << zoom) - 1 - coord.y);
            if (that.vars.layerIndex < 0 || zoom < 12 || zoom > 16 ||
                x < that.tileX(that.vars.layers[that.vars.layerIndex].bounds[0], zoom) ||
                x > that.tileX(that.vars.layers[that.vars.layerIndex].bounds[2], zoom) ||
                coord.y > that.tileY(that.vars.layers[that.vars.layerIndex].bounds[1], zoom) ||
                coord.y < that.tileY(that.vars.layers[that.vars.layerIndex].bounds[3], zoom) ||
                that.existsInStruct([that.vars.layers[that.vars.layerIndex].year, '' + zoom, '' + x, tmsY], that.empty)
            ) {
                return 'http://tile.openstreetmap.org/' + zoom + '/' + x + '/' + coord.y + '.png';
            } else {
                return that.vars.vanalinnadTiles + 'raster/places/' + that.vars.site + '/' +
                    that.vars.layers[that.vars.layerIndex].year + '/' + zoom + '/' + x + '/' + tmsY + '.jpg';
            }
        },
        tileSize: new google.maps.Size(256, 256),
        name: 'vanalinnad.mooo.com',
        maxZoom: 16
    });
    this.changeIndex = function (index) {
        this.vars.layerIndex = index;
        this.refreshMap();
    };
    this.showControls = function () {
        $(that.citySelection).show();
        $(that.yearSelection).show();
    };
    this.hideControls = function () {
        $(that.citySelection).hide();
        $(that.yearSelection).hide();
    };
    this.getCityData = function (callback) {
        $.ajax({
            url: that.vars.vanalinnadPrefix + 'vector/places/' + that.vars.site + '/empty.json',
            dataType: 'json'
        }).done(function (data) {
            that.empty = data;
            $.ajax({
                url: that.vars.vanalinnadPrefix + 'vector/places/' + that.vars.site + '/layers.xml',
                dataType: 'xml'
            }).done(function (data) {
                if (!('coords' in that.vars)) {
                    var bounds = that.getXmlValue(data, 'bounds').split(',');
                    that.vars.coords = [
                        (parseFloat(bounds[0]) + parseFloat(bounds[2])) / 2,
                        (parseFloat(bounds[1]) + parseFloat(bounds[3])) / 2,
                        parseInt(that.getXmlValue(data, 'minzoom'), 10)
                    ];
                }
                var l = data.getElementsByTagName('layer'),
                    ll,
                    i;
                that.vars.layers = [];
                for (i = 0; i < l.length; i += 1) {
                    if (l[i].getAttribute('type') === 'tms') {
                        that.vars.layers.push({
                            year: l[i].getAttribute('year'),
                            bounds: l[i].getAttribute('bounds').split(',')
                        });
                        ll = that.vars.layers.length - 1;
                        that.vars.layers[ll].bounds = [
                            parseFloat(that.vars.layers[ll].bounds[0]),
                            parseFloat(that.vars.layers[ll].bounds[1]),
                            parseFloat(that.vars.layers[ll].bounds[2]),
                            parseFloat(that.vars.layers[ll].bounds[3])
                        ];
                    }
                }
                callback();
            });
        });
    };
    this.buildVanalinnadMapYearControl = function () {
        var vanalinnadYearSelection = $('<select class="ajapaik-map-vanalinnad-year-select"></select>');
        $.each(that.vars.layers, function (k, v) {
            var vanalinnadYearSelectionOption = $('<option value="' + k + '">' + v.year + '</option>');
            if (that.vars.layerIndex === k) {
                vanalinnadYearSelectionOption.prop('selected', true);
            }
            vanalinnadYearSelection.append(vanalinnadYearSelectionOption);
        });

        vanalinnadYearSelection.change(function () {
            that.changeIndex($(this).val());
        });

        that.yearSelection = vanalinnadYearSelection.get(0);

        that.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(that.yearSelection);
    };
    this.buildVanalinnadMapCityControl = function () {
        $('#ajapaik-map-vanalinnad-city-select').remove();
        var vanalinnadCitySelection = $('<select class="ajapaik-map-vanalinnad-city-select"></select>');
        $.each(that.vanalinnadCitiesMap, function (k, v) {
            var vanalinnadCitySelectionOption = $('<option value="' + v + '">' + k + '</option>');
            if (that.vars.site === v) {
                vanalinnadCitySelectionOption.prop('selected', true);
            }
            vanalinnadCitySelection.append(vanalinnadCitySelectionOption);
        });

        vanalinnadCitySelection.change(function () {
            that.vars.site = $(this).val();
            that.getCityData(function () {
                that.changeIndex(0);
            });
        });
        
        that.citySelection = vanalinnadCitySelection.get(0);

        that.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(that.citySelection);
    };
    this.refreshMap = function () {
        // Hack to make Google Maps refresh tiles
        var currentZoom = that.map.zoom;
        that.map.setZoom(currentZoom - 1);
        setTimeout(function () {
            that.map.setZoom(currentZoom);
        }, 0);
    };
    this.tileX = function (coord, zoom) {
        return Math.floor((coord + 180) / 360 * (1 << zoom));
    };
    this.tileY = function (coord, zoom) {
        return Math.floor((1 - Math.log(Math.tan(coord * Math.PI / 180) + 1 /
                Math.cos(coord * Math.PI / 180)) / Math.PI) / 2 * (1 << zoom));
    };
    this.existsInStruct = function (path, struct) {
        var pointer = struct,
            lastIndex = 3,
            i,
            lastValue;
        for (i = 0; i < lastIndex; i += 1) {
            if (pointer.hasOwnProperty(path[1])) {
                pointer = pointer[path[i]];
            } else {
                return false;
            }
        }
        lastValue = isNaN(pointer[0]) ? pointer[0][0] : pointer[0];
        if (path[lastIndex] < lastValue) {
            return false;
        }
        lastValue = pointer.length - 1;
        lastValue = isNaN(pointer[lastValue]) ? pointer[lastValue][1] : pointer[lastValue];
        if (path[lastIndex] > lastValue) {
            return false;
        }
        for (i = 0; i < pointer.length; i += 1) {
            if (isNaN(pointer[i])) {
                if (path[lastIndex] >= pointer[i][0] && path[lastIndex] <= pointer[i][1]) {
                    return true;
                }
                lastValue = pointer[i][1];
            } else {
                if (pointer[i] == path[lastIndex]) {
                    return true;
                }
                lastValue = pointer[i];
            }
        }

        return false;
    };
    this.getXmlValue = function (xmlDocument, tagname) {
        var index = (arguments.length > 2 ) ? arguments[2] : 0,
            tags = xmlDocument.getElementsByTagName(tagname);
        return index < tags.length && tags[index].childNodes.length > 0 ? tags[index].childNodes[0].nodeValue : '';
    };
}