'use strict';

/*jslint browser: true */
/*global window */

var TIME_TO_CACHE_IN_MINUTES = 60;

var cacheKeys = {
    objectClasses: 'OBJECT_CLASSES'
};

function removeData(key) {
    window.localStorage.removeItem(key);
}

function getTimeStampInSeconds() {
    return Math.floor(new Date().getTime() / 1000);
}

function storeData(key, data) {
    window.localStorage.setItem(key, JSON.stringify({
        timestamp: getTimeStampInSeconds(),
        data: data
    }));
}

function getData(key) {
    var item = window.localStorage.getItem(key);

    if (item) {
        return JSON.parse(item).data;
    }

    return null;
}

function getDataWithExpirationValidation(key) {
    var data = window.localStorage.getItem(key);

    if (!data) {
        return null;
    }

    var dataObject = JSON.parse(data);
    var currentTimeStamp = getTimeStampInSeconds();

    var secondsElapsedSinceCaching = currentTimeStamp - parseFloat(dataObject.timestamp);
    var minutesElapsedSinceCaching = secondsElapsedSinceCaching / 60;

    if (minutesElapsedSinceCaching >= TIME_TO_CACHE_IN_MINUTES) {
        removeData(key);
        return null;
    }

    return getData(key);
}
