
window.refreshUpdatedImageLight = function(img) {
    if ($(img).length > 0) {
        let url = $(img).attr('src');
        if (url) {
            url = url.split('?timestamp')[0] + '?timestamp=' + Date.now();
            $(img).attr("src", url);
        }
    }
}

window.refreshUpdatedImage = function(img) {
    let clone = $(img).clone();
    if (clone !== undefined) {
        let url = clone.attr('src');
        if (url) {
            url = url.split('?timestamp')[0] + '?timestamp=' + Date.now();
            clone.attr("src", url);
            clone.removeClass();
            clone.css({'padding-bottom': '', 'padding-top': ''});
            clone.css({'padding-right': '', 'padding-left': ''});
            $(img).replaceWith(clone);
        }
    }
}