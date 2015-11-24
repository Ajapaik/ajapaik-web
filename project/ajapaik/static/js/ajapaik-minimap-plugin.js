(function () {
    'use strict';
    /*global $*/
    /*global google*/
    // TODO: Pack mini-map shit into this, just like geotagger
    var AjapaikMinimap = function (node, options) {
        var that = this;
        this.node = node;
        // Not used currently
        this.options = $.extend({

        }, options);
        // Inner workings
        this.arrowIcon = {
            path: 'M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            rotation: 0,
            scale: 1.5,
            anchor: new google.maps.Point(12, 12)
        };
        this.locationIcon = {
            path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            scale: 1.5,
            anchor: new google.maps.Point(12, 18)
        };
        this.currentIcon = null;
        this.UI = $([
            '<div id="ajapaik-minimap-disabled-overlay"></div>',
            '<div id="ajapaik-photo-modal-map-canvas"></div>'
        ].join('\n'));
        $(this.node).html(this.UI);
    };
    AjapaikMinimap.prototype = {
        constructor: AjapaikMinimap,
        initializeMap: function () {

        }
    };
    $.fn.AjapaikMinimap = function (options) {
        return this.each(function () {
            $(this).data('AjapaikMinimap', new AjapaikMinimap(this, options));
        });
    };
}());