var vanalinnadCitiesMap = [
        {name: 'Haapsalu', latitude: 58.9394, longitude: 23.5408},
        {name: 'Kuressaare', latitude: 58.2500, longitude: 22.4833},
        {name: 'Narva', latitude: 59.3758, longitude: 28.1961}
        //{name: 'Paide', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Parnu', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Rakvere', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Tallinn', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Tartu', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Valga', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Viljandi', latitude: 58.9394, longitude: 23.5408},
        //{name: 'Voru', latitude: 58.9394, longitude: 23.5408}
    ],
    vanalinnadCitiesCount = vanalinnadCitiesMap.length,
    nearestCity;

function VanalinnadGooglemApi(inputParams) {
    this.empty = {};
    this.vars = {
        layers: [],
        layerIndex: -1,
        site: '',
        vanalinnadPrefix: '/vanalinnad.mooo.com/',
        override: ['layerIndex', 'site', 'vanalinnadPrefix', 'coords', 'vanalinnadTiles']
    };

    this.changeDiff = function (diff) {
        this.vars.layerIndex += diff;
        if (this.vars.layerIndex > this.vars.layers.length - 1) {
            this.vars.layerIndex = -1;
        }
        if (this.vars.layerIndex < -1) {
            this.vars.layerIndex = this.vars.layers.length - 1;
        }
        this.refreshMap();
    };

    this.calculateNearestVanalinnadCity = function () {
        var i,
            minDistance = 9999999,
            currentDistance,
            currentMapCenter = this.map.getCenter();
        for (i = 0; i < vanalinnadCitiesCount; i += 1) {
            currentDistance = Math.haversineDistance(currentMapCenter, vanalinnadCitiesMap[i]);
            console.log(currentDistance);
            if (currentDistance < minDistance) {
                minDistance = currentDistance;
                nearestCity = vanalinnadCitiesMap[i].name;
            }
        }
    };

    this.changeIndex = function (index) {
        this.vars.layerIndex = index;
        this.refreshMap();
    };

    this.getYear = function () {
        if (this.vars.layerIndex < 0) {
            var now = new Date();
            return now.getFullYear();
        }
        return this.vars.layers[this.vars.layerIndex].year;
    };

    this.refreshMap = function () {
        // Hack to make Google Maps refresh tiles
        var that = this;
        this.map.setZoom(this.map.zoom + 1);
        setTimeout(function () {
            that.map.setZoom(that.map.zoom - 1);
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

        var i;
        for (i in inputParams) {
            if (jQuery.inArray(i, this.vars.override)) {
                this.vars[i] = inputParams[i];
            }
        }
        if (!('vanalinnadTiles' in this.vars)) {
            this.vars.vanalinnadTiles = this.vars.vanalinnadPrefix;
        }

        if ('site' in inputParams) {

            var vgmapi = this;

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
                            parseInt(vgmapi.getXmlValue(data, 'minzoom'))
                        ];
                    }
                    var l = data.getElementsByTagName('layer'),
                        ll;
                    for (i = 0; i < l.length; i++) {
                        if (l[i].getAttribute('type') == 'tms') {
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
                });
            });

        }
    };

    this.init();
}