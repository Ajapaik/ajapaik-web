function postPictureCategory(id, category) {
    console.log(id);
    category = category.split(" ")[0];
    console.log(category);
    console.log("I am in post");
    $.ajax({
        type: 'GET',
        // url: 'https://staging.ajapaik.ee/predict/image_2.jpg',
        url: 'http://localhost:8000/photo-thumb-path/' + id,
        // beforeSend: function (xhr) {
        //     xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        // },
        headers: {
            'Content-Type': 'text/plain'
        },
        success: function (response) {
            console.log("====");
            console.log(response);
            imageUrl = String(response).replaceAll("/", "-");
            console.log(imageUrl);
            $.ajax({
                type: 'POST',
                url: 'https://anna.ajapaik.ee/predict',
                // url: 'http://localhost:7000/predict/' + imageUrl,
                // beforeSend: function (xhr) {
                //     xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
                // },
                data: {'category': category, 'imageUrl': imageUrl},
                headers: {
                    'Content-Type': 'application/json',
                },
                success: function (response) {
                    console.log("SUCCESS");
                    $("#ajp-category-confirmation").html("Done");
                },
                error: function (error) {
                    console.log("Some error has occured: IN");
                    console.log(error)
                }
            });
        },
        error: function (error) {
            console.log("Some error has occured: OUT");
            console.log(error)
        }
    });
}