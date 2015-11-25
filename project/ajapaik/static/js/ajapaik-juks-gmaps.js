var vgmapi = new VanalinnadGooglemApi({});
vgmapi.vars.site = 'Tallinn';

var juksMapType = new google.maps.ImageMapType({
    getTileUrl: function (coord, zoom) {
        // "Wrap" x (longitude) at 180th meridian properly
        // NB: Don't touch coord.x because coord param is by reference, and changing it's x property breaks something in Google's lib
        var tilesPerGlobe = 1 << zoom;
        var x = coord.x % tilesPerGlobe;
        if (x < 0) {
            x = tilesPerGlobe + x;
        }
        // Wrap y (latitude) in a like manner if you want to enable vertical infinite scroll
        var tmsY = ((1 << zoom) - 1 - coord.y);
        if (vgmapi.vars.layerIndex < 0 || zoom < 12 || zoom > 16 ||
            x < vgmapi.tileX(vgmapi.vars.layers[vgmapi.vars.layerIndex].bounds[0], zoom) ||
            x > vgmapi.tileX(vgmapi.vars.layers[vgmapi.vars.layerIndex].bounds[2], zoom) ||
            coord.y > vgmapi.tileY(vgmapi.vars.layers[vgmapi.vars.layerIndex].bounds[1], zoom) ||
            coord.y < vgmapi.tileY(vgmapi.vars.layers[vgmapi.vars.layerIndex].bounds[3], zoom) ||
            vgmapi.existsInStruct([vgmapi.vars.layers[vgmapi.vars.layerIndex].year, '' + zoom, '' + x, tmsY], vgmapi.empty)
        ) {
            return "http://tile.openstreetmap.org/" + zoom + "/" + x + "/" + coord.y + ".png";
        } else {
            return vgmapi.vars.vanalinnadTiles + 'raster/places/' + vgmapi.vars.site + '/' +
                vgmapi.vars.layers[vgmapi.vars.layerIndex].year + '/' + zoom + "/" + x + "/" + tmsY + ".jpg";
        }
    },
    tileSize: new google.maps.Size(256, 256),
    name: 'vanalinnad.mooo.com',
    maxZoom: 16
});

function VanalinnadGooglemApi() {
    this.empty = {};
    this.vars = {
        layers: [],
        layerIndex: -1,
        site: '',
        vanalinnadPrefix: '/vanalinnad.mooo.com/'
    };

    var vanalinnadCitiesMap = {
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

    this.changeIndex = function (index) {
        this.vars.layerIndex = index;
        this.refreshMap();
    };

    this.showControls = function () {
        if (this.yearSelection) {
            this.yearSelection.show();
        }
        if (this.citySelection) {
            this.citySelection.show();
        }
    };

    this.hideControls = function () {
        if (this.yearSelection) {
           this.yearSelection.hide();
        }
        if (this.citySelection) {
            this.citySelection.hide();
        }
    };

    this.getYear = function () {
        if (this.vars.layerIndex < 0) {
            var now = new Date();
            return now.getFullYear();
        }
        return this.vars.layers[this.vars.layerIndex].year;
    };

    this.getCityData = function () {
        $.ajax({
            url: vgmapi.vars.vanalinnadPrefix + 'vector/places/' + vgmapi.vars.site + '/empty.json',
            dataType: 'json'
        }).done(function (data) {
            vgmapi.empty = data;
            $.ajax({
                url: vgmapi.vars.vanalinnadPrefix + 'vector/places/' + vgmapi.vars.site + '/layers.xml',
                dataType: 'xml'
            }).done(function (data) {
                if (!('coords' in vgmapi.vars)) {
                    var bounds = vgmapi.getXmlValue(data, 'bounds').split(',');
                    vgmapi.vars.coords = [
                        (parseFloat(bounds[0]) + parseFloat(bounds[2])) / 2,
                        (parseFloat(bounds[1]) + parseFloat(bounds[3])) / 2,
                        parseInt(vgmapi.getXmlValue(data, 'minzoom'), 10)
                    ];
                }
                var l = data.getElementsByTagName('layer'),
                    ll,
                    i;
                vgmapi.vars.layers = [];
                for (i = 0; i < l.length; i += 1) {
                    if (l[i].getAttribute('type') === 'tms') {
                        vgmapi.vars.layers.push({
                            year: l[i].getAttribute('year'),
                            bounds: l[i].getAttribute('bounds').split(',')
                        });
                        ll = vgmapi.vars.layers.length - 1;
                        vgmapi.vars.layers[ll].bounds = [
                            parseFloat(vgmapi.vars.layers[ll].bounds[0]),
                            parseFloat(vgmapi.vars.layers[ll].bounds[1]),
                            parseFloat(vgmapi.vars.layers[ll].bounds[2]),
                            parseFloat(vgmapi.vars.layers[ll].bounds[3])
                        ];
                    }
                }
                vgmapi.changeIndex(0);
                vgmapi.buildVanalinnadMapYearControl();
            });
        });
    };

    this.buildVanalinnadMapYearControl = function () {
        $('#ajapaik-map-vanalinnad-year-select').remove();
        var vanalinnadYearSelection = $('<select id="ajapaik-map-vanalinnad-year-select"></select>');
        $.each(vgmapi.vars.layers, function (k, v) {
            var vanalinnadYearSelectionOption = $('<option value="' + k + '">' + v.year + '</option>');
            if (vgmapi.vars.layerIndex === k) {
                vanalinnadYearSelectionOption.prop('selected', true);
            }
            vanalinnadYearSelection.append(vanalinnadYearSelectionOption);
        });

        vanalinnadYearSelection.change(function () {
            console.log('year changed');
            vgmapi.changeIndex($(this).val());
        });

        this.yearSelection = vanalinnadYearSelection;

        vgmapi.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(vanalinnadYearSelection.get(0));
    };

    this.buildVanalinnadMapCityControl = function () {
        var vanalinnadCitySelection = $('<select id="ajapaik-map-vanalinnad-city-select"></select>');
        $.each(vanalinnadCitiesMap, function (k, v) {
            var vanalinnadCitySelectionOption = $('<option value="' + v + '">' + k + '</option>');
            if (vgmapi.vars.site === v) {
                vanalinnadCitySelectionOption.prop('selected', true);
            }
            vanalinnadCitySelection.append(vanalinnadCitySelectionOption);
        });

        vanalinnadCitySelection.change(function () {
            console.log('city changed');
            vgmapi.vars.site = $(this).val();
            vgmapi.getCityData();
        });

        this.citySelection = vanalinnadCitySelection;

        vgmapi.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(vanalinnadCitySelection.get(0));
    };

    this.refreshMap = function () {
        // Hack to make Google Maps refresh tiles
        var that = this,
            currentZoom = this.map.zoom;
        this.map.setZoom(currentZoom - 1);
        setTimeout(function () {
            that.map.setZoom(currentZoom);
        }, 0);
    };

    this.tileX = function (coord, zoom) {
        return Math.floor((coord + 180) / 360 * (1 << zoom));
    };

    this.tileY = function (coord, zoom) {
        return Math.floor((1 - Math.log(Math.tan(coord * Math.PI / 180) + 1 / Math.cos(coord * Math.PI / 180)) / Math.PI) / 2 * (1 << zoom));
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

    this.init = function () {
        if (!('vanalinnadTiles' in this.vars)) {
            this.vars.vanalinnadTiles = this.vars.vanalinnadPrefix;
        }

        if (this.vars.site) {
            var vgmapi = this;
            vgmapi.getCityData();
        }
    };
}