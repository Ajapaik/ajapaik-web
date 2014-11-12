(function ($) {






    function monitor(element, options) {
        var item = { element: element, options: options, invp: false };
        _watch.push(item);
        return item;
    }

    function unmonitor(item) {
        for (var i = 0; i < _watch.length; i++) {
            if (_watch[i] === item) {
                _watch.splice(i, 1);
                item.element = null;
                break;
            }
        }
        console.log(_watch);
    }

    var pluginName = 'scrolledIntoView',
        settings = {
            scrolledin: null,
            scrolledout: null
        }


    $.fn[pluginName] = function (options) {

        var options = $.extend({}, settings, options);

        this.each(function () {

            var $el = $(this),
                instance = $.data(this, pluginName);

            if (instance) {
                instance.options = options;
            } else {
                $.data(this, pluginName, monitor($el, options));
                $el.on('remove', $.proxy(function () {

                    $.removeData(this, pluginName);
                    unmonitor(instance);

                }, this));
            }
        });

        return this;
    }


})(jQuery);