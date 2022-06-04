function getPictureCategory(id) {
    console.log(id);
    $.ajax({
        type: 'GET',
        url: 'https://staging.ajapaik.ee/predict/image_2.jpg',
        // beforeSend: function (xhr) {
        //     // xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        // },
        headers: {
            'Content-Type': 'application/json'
        },
        success: function (response) {
            const category = response["category"];
            const probability = parseFloat(response["probability"]).toFixed(2) * 100;
            $("#ajp-probability1").html(category + " (" + probability + "%) :");
        },
        error: function (error) {
            console.log("Some error has occured");
            console.log(error)
        }
    });
}