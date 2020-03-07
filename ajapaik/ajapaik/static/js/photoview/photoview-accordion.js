'use strict';

$(document).ready(function () {
    function setMoreAndLessIconVisibility(target) {
        var isCollapsed = target.hasClass('collapsed');

        var showMoreIcon = target.find('[data-icon-type="more"]');
        var showLessIcon = target.find('[data-icon-type="less"]');

        if (isCollapsed) {
            showMoreIcon.show();
            showLessIcon.hide();
        } else {
            showMoreIcon.hide();
            showLessIcon.show();
        }
    }

    function addClassChangeListenersToCollapseTitles() {
        $('[data-toggle="collapse"]').each(function () {
            var target = this;
            var observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    if (mutation.attributeName === 'class') {
                        var mutationTarget = $(mutation.target);
                        setMoreAndLessIconVisibility(mutationTarget);
                    }
                });
            });

            observer.observe(target, {
                attributes: true
            });
        });
    }

    addClassChangeListenersToCollapseTitles();
});