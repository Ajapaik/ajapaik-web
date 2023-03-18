function getPictureCategoryCategories(photoId, callback) {
    var onSuccess = function (response) {
        callback(determinePictureCategory(response.data));
    };
    getRequest(
        '/object-categorization/get-latest-category/' + photoId + '/',
        null,
        null,
        constants.translations.queries.GET_CATEGORY_FAILED,
        onSuccess
    );
}

function determinePictureCategory(responseData) {
    var responseDict = {}
    var category;

    for (let i = 0; i < responseData.length; i++) {
        var data = responseData[i]
        var model = data["model"];
        if (model === "ajapaik.photoscenesuggestion") {
            category = data["fields"]["scene"]
            if (category === 0) {
                responseDict["scene"] = "interior";
            } else {
                responseDict["scene"] = "exterior";
            }
        }
        if (model === "ajapaik.photoviewpointelevationsuggestion") {
            category = data["fields"]["viewpoint_elevation"]
            if (category === 0) {
                responseDict["viewpoint_elevation"] = "ground";
            } else if (category === 1) {
                responseDict["viewpoint_elevation"] = "raised";
            } else {
                responseDict["viewpoint_elevation"] = "areal";
            }
        }

    }
    return responseDict;
}