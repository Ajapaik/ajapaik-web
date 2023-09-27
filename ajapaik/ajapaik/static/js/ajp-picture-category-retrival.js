function getImageCategory(photoId, callback) {
    let onSuccess = function (response) {
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
    let responseDict = {};
    for (let data of responseData) {
        let fields = data["fields"];
        if ("scene" in fields) {
            if (fields["scene"] === 0) {
                responseDict["scene"] = "interior";
            } else {
                responseDict["scene"] = "exterior";
            }
        }
        if ("viewpoint_elevation" in fields) {
            if (fields["viewpoint_elevation"] === 0) {
                responseDict["viewpoint_elevation"] = "ground";
            } else if (fields["viewpoint_elevation"] === 1) {
                responseDict["viewpoint_elevation"] = "raised";
            } else if (fields["viewpoint_elevation"] === 2) {
                responseDict["viewpoint_elevation"] = "areal";
            }
        }
    }
    return responseDict;
}

function sendCategoryFeedback(photoId, category, categoryValue) {
    let payload = {
        "photo_id": photoId
    };

    if (category === "scene") {
        if (categoryValue === "interior") {
            payload["scene_to_alternate"] = 0
        } else if (categoryValue === "exterior") {
            payload["scene_to_alternate"] = 1
        }
    } else if (category === "view-point-elevation") {
        if (categoryValue === "ground") {
            payload["viewpoint_elevation_to_alternate"] = 0
        } else if (categoryValue === "raised") {
            payload["viewpoint_elevation_to_alternate"] = 1
        } else {
            payload["viewpoint_elevation_to_alternate"] = 2
        }
    }

    const onSuccess = function () {
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
