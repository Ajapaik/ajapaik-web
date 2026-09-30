(function ($) {
    'use strict';

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker.register('/sw.js').catch(function (err) {
                console.debug('PWA ServiceWorker registration failed:', err);
            });
        });
    }

    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

    // If standalone PWA app opened on root without params, redirect to rephoto mode automatically
    if (isStandalone && window.location.pathname === '/' && !window.location.search) {
        window.location.replace('/?mode=rephoto');
    }

    // PWA Install Prompt handling
    let deferredPrompt = null;

    // Android / Chromium
    window.addEventListener('beforeinstallprompt', function (e) {
        e.preventDefault();
        deferredPrompt = e;

        // Check if user has previously dismissed or installed
        if (localStorage.getItem('ajp_pwa_dismissed') === '1') {
            return;
        }
        if (isStandalone) {
            return;
        }

        // Show banner after brief delay
        setTimeout(function () {
            if (localStorage.getItem('ajp_pwa_dismissed') !== '1') {
                $('#ajp-pwa-install-banner').removeClass('d-none');
            }
        }, 1500);
    });

    // Handle install click
    $(document).on('click', '#ajp-pwa-install-btn', async function () {
        $('#ajp-pwa-install-banner').addClass('d-none');
        localStorage.setItem('ajp_pwa_dismissed', '1');
        if (deferredPrompt) {
            deferredPrompt.prompt();
            try {
                await deferredPrompt.userChoice;
            } catch (err) {
                console.debug('PWA userChoice error:', err);
            }
            deferredPrompt = null;
        }
    });

    // Handle dismiss click (permanent - never show again!)
    $(document).on('click', '.ajp-pwa-dismiss-btn', function () {
        $('#ajp-pwa-install-banner').addClass('d-none');
        $('#ajp-pwa-ios-banner').addClass('d-none');
        localStorage.setItem('ajp_pwa_dismissed', '1');
    });

    // iOS Safari guidance
    $(document).ready(function () {
        if (isStandalone || localStorage.getItem('ajp_pwa_dismissed') === '1') {
            return;
        }

        const isIos = /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
        const isSafari = /^((?!chrome|android).)*safari/i.test(window.navigator.userAgent);

        if (isIos && isSafari) {
            // Show subtle iOS instruction banner after 3 seconds on mobile
            setTimeout(function () {
                if (localStorage.getItem('ajp_pwa_dismissed') !== '1') {
                    $('#ajp-pwa-ios-banner').removeClass('d-none');
                }
            }, 3000);
        }
    });
})(jQuery);
