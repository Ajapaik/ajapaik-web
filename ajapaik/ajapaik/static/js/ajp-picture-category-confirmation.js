function postPictureCategory(id, category) {
    category = category.split(" ")[0];
    console.log(id);
    console.log(category);
    console.log("I am in post");
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/photo-thumb-path/' + id,
        headers: {
            'Content-Type': 'text/plain'
        },
        success: function (response) {
            imageUrl = String(response).replaceAll("/", "-");
            $.ajax({
                type: 'POST',
                url: 'https://anna.ajapaik.ee/predict',
                data: {'category': category, 'image_url': imageUrl},
                headers: {
                    'Content-Type': 'application/json',
                },
                success: function (response) {
                    console.log("SUCCESS");
                    $("#ajp-category-confirmation").html("Done");
                },
                error: function (error) {
                    console.log("FAILURE: IN");
                    console.log(error)
                }
            });
        },
        error: function (error) {
            console.log("FAILURE: OUT");
            console.log(error)
        }
    });
}