(function () {
    'use strict';
    window.docCookies = {
        getItem: function (sKey) {
            return decodeURIComponent(document.cookie.replace(new RegExp('(?:(?:^|.*;)\\s*' + encodeURIComponent(sKey)
                .replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\=\\s*([^;]*).*$)|^.*$'), '$1')) || null;
        },
        setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
            if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
                return false;
            }
            var sExpires = '';
            if (vEnd) {
                switch (vEnd.constructor) {
                case Number:
                    sExpires = vEnd === Infinity ? '; expires=Fri, 31 Dec 9999 23:59:59 GMT' : '; max-age=' + vEnd;
                    break;
                case String:
                    sExpires = '; expires=' + vEnd;
                    break;
                case Date:
                    sExpires = '; expires=' + vEnd.toUTCString();
                    break;
                }
            }
            document.cookie = encodeURIComponent(sKey) + '=' + encodeURIComponent(sValue) + sExpires +
                (sDomain ? '; domain=' + sDomain : '') + (sPath ? '; path=' + sPath : '') + (bSecure ? '; secure' : '');
            return true;
        },
        removeItem: function (sKey, sPath, sDomain) {
            if (!sKey || !this.hasItem(sKey)) {
                return false;
            }
            document.cookie = encodeURIComponent(sKey) + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT' +
                (sDomain ? '; domain=' + sDomain : '') + (sPath ? '; path=' + sPath : '');
            return true;
        },
        hasItem: function (sKey) {
            return (new RegExp('(?:^|;\\s*)' + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\='))
                .test(document.cookie);
        }
    };
    $(document).ready(function () {
        if (!docCookies.hasItem('ajapaik_agreed_to_cookies')) {
            $('#cookie-notice-container').show();
        } else {
            $('#cookie-notice-container').hide();
        }
    });
    window.setEUCookie = function () {
        docCookies.setItem('ajapaik_agreed_to_cookies', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        $('#cookie-notice-container').hide();
    };
}());