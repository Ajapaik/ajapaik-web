(function($) {
  
  $.jQee = function(keys, cb) {
    var o = $.jQee.defaults;
    if (typeof(keys) === 'object') {
      o = $.extend({}, o, keys);
    } else {
      o.keys = keys;
      o.callback = cb;
    }
    o.keys = o.keys.replace('rightclick', 'contextmenu');
    $.each(['click','dblclick','hover','mousedown','mouseenter','mouseleave', 'tapone', 'taptwo', 'tapthree', 'swipe',
            'mousemove','mouseout','mouseover','mouseup','contextmenu', 
            'swipeup','swipedown','swipeleft','swiperight','swiperightup','swiperightdown',
            'swipeleftup','swipeleftdown','swipeone','swipetwo','swipethree','swipefour',
            'swipemove','orientationchange','pinch','rotate'], 
      function(k,e) {
        if (/textarea|select/i.test($(o.selector).get(0).tagName) || $(o.selector).is('[type=text]') || $(o.selector).prop('contenteditable') == 'true' ) {
        } else {
          if (o.selector !== $(document) && $(o.selector).get(0).tagName !== undefined) {
            if ($(o.selector).attr('tabindex') < 1) {
              $(o.selector).attr("tabindex", 1000+k);
              $(o.selector).css("outline", 'none');
            }
          }
        }
        if (o.keys.indexOf(e.toLowerCase()) != -1) $(o.selector).bind(e, o.callback);        
      }
    );    
    $(o.selector).bind(o.event, o.keys, o.callback);
    $.jQee.active[o.keys] = o;
  };
  
  $.jQee.active = {};
  
  $.jQee.unbind = function(keys) {
    keys = keys.toLowerCase();
    var keyObj = $.jQee.active[keys];
    if (keyObj !== undefined) {
      $(keyObj.selector).unbind(keyObj.event, keyObj.callback);
      delete $.jQee.active[keys];
    }
  }
  
  $.jQee.defaults = {
    selector: document,
    event: 'keydown'
  };
  
  $.fn.jQee = function (keys, cb) {
    this.each(function(v,el) {
      $.jQee({
        keys: keys,
        callback: cb,
        selector: el
      });
    });
    return this;
  }

  $.jQee.specialMap = {16:'shift',17:'ctrl',9:'tab',20:'caps',18:'alt',27:'esc',244:'meta',
    112:'f1',113:'f2',114:'f3',115:'f4',116:'f5',117:'f6',118:'f7',119:'f8',120:'f9',
    121:'f10',122:'f11',123:'f12',45:'insert',36:'home',35:'end',33:'pageup',34:'pagedown',
    19:'pause',145:'scroll',144:'num',37:'left',38:'up',39:'right',40:'down',111:'/',
    106:'*',109:'-',107:'+',110:'.',8:'backspace',32:'space', 13:'enter'};
  
  $.jQee.shiftMap = {
      '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', 
      '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', ';': ': ', '\'': '"', ',': '<', 
      '.': '>',  '/': '?',  '\\': '|'
  };

  $(function() {
    $.each($('a'), function(a) {
      var $this = $(this), shortcut, target, url;
      shortcut = $this.attr('data-key');
      if (shortcut !== undefined && url !== "#") {
        url = $this.attr('href'),
        target = $this.attr('target') || '_self';
        $this.attr('title', 'Keyboard Shortcut: ' + shortcut);
        $.jQee(shortcut, function(e) {
          window.open(url,target);
        });
      }
    });
  });
  
  $.each(['keydown','keyup','keypress'], function() {
    $.event.special[this] = { 
      add: function (obj) {
      
        if (typeof obj.data !== "string")	return;

        var originalHandler = obj.handler,
            keys = obj.data.toLowerCase().split(" ");
        
        obj.handler = function( event ) {
          if (this !== event.target && (/textarea|select/i.test(event.target.nodeName) ||
            event.target.type === "text" || $(event.target).prop('contenteditable') == 'true' )) {
            return;
          }
          var special = event.type !== "keypress" && $.jQee.specialMap[event.which],
              character = String.fromCharCode(event.which).toLowerCase(),
              modif = "", 
              i,
              possible = {};

          if (event.altKey && special !== "alt") modif += "alt+";
          if (event.ctrlKey && special !== "ctrl") modif += "ctrl+";
          if (event.metaKey && !event.ctrlKey && special !== "meta" ) modif += "meta+";
          if (event.shiftKey && special !== "shift") modif += "shift+";

          if (special) {
            possible[modif + special] = true;
          } else {
            possible[modif + character] = true;
            possible[modif + $.jQee.shiftMap[character]] = true;
            if ( modif === "shift+" ) possible[$.jQee.shiftMap[character]] = true;
          }
          for(i=0, l=keys.length; i < l; i++) {
            if(possible[keys[i]]) return originalHandler.apply(this,arguments);
          }
        };
      }
    };
	});

})(jQuery);