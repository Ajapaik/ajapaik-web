function VanalinnadGooglemApi(inputParams) {
    this.map = {};
    this.empty = {};
    this.vars = {
        layers: [],
        layerIndex: -1,
        site: '',
        vanalinnadPrefix: 'http://juks.alkohol.ee/tools/vanalinnad/',
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
    }

    this.changeIndex = function (index) {
        this.vars.layerIndex = index;
        this.refreshMap();
    }

    this.getYear = function () {
        if (this.vars.layerIndex < 0) {
            var now = new Date();
            return now.getFullYear();
        } else {
            return this.vars.layers[this.vars.layerIndex].year;
        }
    }

    this.refreshMap = function () {
        var coords = this.map.getCenter();
        coords = [coords.K, coords.G, this.map.getZoom()];
        this.map = null;
        this.createMap(coords);
        this.drawVectorLayer();
    }

    this.tileX = function (coord, zoom) {
        return Math.floor((coord + 180) / 360 * (1 << zoom));
    }

    this.tileY = function (coord, zoom) {
        return Math.floor((1 - Math.log(Math.tan(coord * Math.PI / 180) + 1 / Math.cos(coord * Math.PI / 180)) / Math.PI) / 2 * (1 << zoom));
    }

    this.existsInStruct = function (path, struct) {
        var pointer = struct;
        var lastIndex = 3;
        var i;
        for (i = 0; i < lastIndex; i++) {
            if (path[i] in pointer) {
                pointer = pointer[path[i]];
            } else {
                return false;
            }
        }

        var lastValue;
        lastValue = isNaN(pointer[0]) ? pointer[0][0] : pointer[0];
        if (path[lastIndex] < lastValue) {
            return false;
        }
        lastValue = pointer.length - 1;
        lastValue = isNaN(pointer[lastValue]) ? pointer[lastValue][1] : pointer[lastValue];
        if (path[lastIndex] > lastValue) {
            return false;
        }

        for (i = 0; i < pointer.length; i++) {
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
    }

    this.getXmlValue = function (xmlDocument, tagname) {
        index = (arguments.length > 2 ) ? arguments[2] : 0;
        tags = xmlDocument.getElementsByTagName(tagname);
        return index < tags.length && tags[index].childNodes.length > 0 ? tags[index].childNodes[0].nodeValue : '';
    }

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
                url: '/juks/empty-json?site=' + vgmapi.vars.site,
                dataType: 'json'
            }).done(function (data) {
                vgmapi.empty = data;
                $.ajax({
                    url: '/juks/layers?site=' + vgmapi.vars.site,
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
                    var l = data.getElementsByTagName('layer');
                    var ll;
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
                    //vgmapi.createMap(vgmapi.vars.coords);
                    //vgmapi.drawVectorLayer();
                });
            });

        } else {
            //this.createMap(inputParams.coords);
        }
    }

    this.init();
}