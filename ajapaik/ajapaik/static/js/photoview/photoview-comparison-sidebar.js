'use strict';

$(document).ready(function () {
    function initializeSidebarControls() {
        var isSharedWithRephoto = $('#comparison-sidebar').data('is-shared-with-rephoto');

        var allTabs = $('#comparison-sidebar-tabs a');
        var totalAmountOfTabs = allTabs.length;
        var numberOfDisabledTabs = allTabs.filter('.disabled').length;
        var firstNonDisabledTab = allTabs
            .filter(function() {
                return !$(this).hasClass('disabled');
            })
            .first();

        if (numberOfDisabledTabs !== totalAmountOfTabs) {
            if (!isSharedWithRephoto) {
                var firstNonDisabledTabId = firstNonDisabledTab.attr('id');
                firstNonDisabledTab.addClass('active');
                $('#tab-content [aria-labelledby=' + firstNonDisabledTabId + ']').addClass('active show');
            }

            $('#open-comparison-sidebar-button').on('click', openSidebar);
            $('#close-comparison-sidebar-button').on('click', closeSidebar);
        } else {
            $('#open-comparison-sidebar-button').addClass('disabled');
        }
    }

    function openSidebar() {
        $('#comparison-sidebar').addClass('photo-comparison-sidebar--opened');
    }

    function closeSidebar() {
        $('#comparison-sidebar').removeClass('photo-comparison-sidebar--opened');
    }

    function setSidebarOpenButtonSizeAndLocation() {
        var buttonWrapper = $('#toggle-comparison-sidebar');
        var header = $('#page-header');

        var headerHeight = header.outerHeight();

        // As CSS applies a 270 degree rotation, then height and width are flipped
        var width = buttonWrapper.outerHeight();
        var height = buttonWrapper.outerWidth();

        var halfOfHeight = height / 2;
        var halfOfWidth = width / 2;

        var horizontalPosition = halfOfWidth - halfOfHeight;
        var verticalPosition = headerHeight + halfOfHeight;

        buttonWrapper.css({
            right: horizontalPosition + 'px',
            top: verticalPosition + 'px',
            display: 'initial'
        });
    }

    function setMenuSizes() {
        var topAndBottomPaddingOfComparisonSidebar = 10;

        var pictureArea = $('#ajapaik-photoview-main-photo-container');
        var tabsArea = $('#comparison-sidebar-tabs');
        var tabsAreaHeight = tabsArea.outerHeight();

        var horizontalAreaLeftToFillAfterPhotoView = ($(window).width() - (pictureArea.offset().left + pictureArea.width())) - 20;
        var photoViewHeight = pictureArea.height();

        var maxRephotoHeightAllowed = photoViewHeight - tabsAreaHeight - topAndBottomPaddingOfComparisonSidebar;

        $('#comparison-sidebar').css({
            'width': horizontalAreaLeftToFillAfterPhotoView + 'px',
            'height': photoViewHeight + 'px'
        });

        $('#ajapaik-photoview-rephoto').css({
            'max-height': maxRephotoHeightAllowed + 'px',
            'min-height': maxRephotoHeightAllowed + 'px'
        });
        $('#similar-photo-large-view').css({
            'max-height': maxRephotoHeightAllowed + 'px',
            'min-height': maxRephotoHeightAllowed + 'px'
        });

        $('#ajapaik-photo-modal-map-container').css('min-height', maxRephotoHeightAllowed + 'px');
    }

    setSidebarOpenButtonSizeAndLocation();
    initializeSidebarControls();

    setMenuSizes();
    $(window).resize(setMenuSizes);
});
