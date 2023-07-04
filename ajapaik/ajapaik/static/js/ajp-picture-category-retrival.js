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

function sendCategoryFeedback(photoId, category, categoryValue) {
    console.log("Persisting category alternation to db")
    let payload = {
        "photo_id": photoId
    };

    if (category === "scene") {
        if (categoryValue === "interior") {
            payload["scene_to_alternate"] = 0
        } else if (categoryValue === "exterior") {
            payload["scene_to_alternate"] = 1
        }
    } else if (category === "view-point") {
        if (categoryValue === "ground") {
            payload["viewpoint_elevation_to_alternate"] = 0
        } else if (categoryValue === "raised") {
            payload["viewpoint_elevation_to_alternate"] = 1
        } else {
            payload["viewpoint_elevation_to_alternate"] = 2
        }
    }

    var onSuccess = function () {
        console.log("It was a success!")
    };

    postRequest(
        '/object-categorization/confirm-latest-category',
        payload,
        constants.translations.queries.POST_CATEGORY_CONFIRMATION_SUCCESS,
        constants.translations.queries.POST_CATEGORY_CONFIRMATION_FAILED,
        onSuccess
    );
}

//TODO: to remove
function sendCategoryConfirmation(photoId, category, categoryValue, confirm) {


    console.log("categoryValue")
    console.log(categoryValue)

    var payload = {
        "photo_id": photoId
        // "viewpoint_elevation_to_confirm": 1,
        // "scene_to_confirm": 1,
        // "viewpoint_elevation_to_reject": 1,
        // "scene_to_reject": 1
    }

    if (category === "scene") {
        if (categoryValue === "interior") {
            confirm === 1 ? payload["scene_to_confirm"] = 0 : payload["scene_to_reject"] = 0
        } else if (categoryValue === "exterior") {
            confirm === 1 ? payload["scene_to_confirm"] = 1 : payload["scene_to_reject"] = 1
        }
    } else if (category === "view-point") {
        if (categoryValue === "ground") {
            confirm === 1 ? payload["viewpoint_elevation_to_confirm"] = 0 : payload["viewpoint_elevation_to_reject"] = 0
        } else if (categoryValue === "raised") {
            confirm === 1 ? payload["viewpoint_elevation_to_confirm"] = 1 : payload["viewpoint_elevation_to_reject"] = 1
        } else {
            confirm === 1 ? payload["viewpoint_elevation_to_confirm"] = 2 : payload["viewpoint_elevation_to_reject"] = 2
        }
    }

    console.log("PALYLOAD")
    console.log(payload)

    var onSuccess = function () {
        console.log("It was a success!")
    };

    postRequest(
        '/object-categorization/confirm-latest-category',
        payload,
        constants.translations.queries.POST_CATEGORY_CONFIRMATION_SUCCESS,
        constants.translations.queries.POST_CATEGORY_CONFIRMATION_FAILED,
        onSuccess
    );
    console.log(photoId);
    console.log(category);
    console.log(confirm);
}

function determinePictureCategory(responseData) {
    var responseDict = {}
    var category;

    for (let i = 0; i < responseData.length; i++) {
        var data = responseData[i]
        var model = data["model"];
        if (model === "ajapaik.photomodelsuggestionresult") {
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