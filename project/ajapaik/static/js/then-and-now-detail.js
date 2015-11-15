(function () {
    'use strict';
    $(document).ready(function () {
        $('.glyphicon-camera').click(function () {
            $('#camera-file-capture').click();
        });
    });
}());


var form = document.getElementById('file-form');
var fileSelect = document.getElementById('file-select');

    function PreviewImage() {
        var oFReader = new FileReader ();
        oFReader.readAsDataURL(document.getElementById("camera-file-capture").files[0]);

        oFReader.onload = function (oFREvent) {
            document.getElementById("uploadPreview").src = oFREvent.target.result;
        };
    };