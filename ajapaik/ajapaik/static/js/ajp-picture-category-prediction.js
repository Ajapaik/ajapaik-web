function getPictureCategory(id) {
    // console.log(id.id);
        console.log("=====");
        $.ajax({
        type: 'GET',
        // url: 'https://staging.ajapaik.ee/predict/image_2.jpg',
        url: 'https://anna.ajapaik.ee/photo-thumb-path/1',
        // beforeSend: function (xhr) {
        //     xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        // },
        headers: {
            'Content-Type': 'text/plain'
        },
        success: function (response) {
            console.log("====");
            console.log(response);
            result = String(response).replaceAll("/", "-");
            console.log(result);
            $.ajax({
                type: 'GET',
                url: 'https://anna.ajapaik.ee/predict/' + result,
                // url: 'http://localhost:7000/predict/' + result,
                // beforeSend: function (xhr) {
                //     xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
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


    // $.ajax({
    //     type: 'GET',
    //     // url: 'https://staging.ajapaik.ee/predict/image_2.jpg',
    //     url: 'http://localhost:7000/predict/' + id,
    //     beforeSend: function (xhr) {
    //         xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
    //     },
    //     headers: {
    //         'Content-Type': 'application/json'
    //     },
    //     success: function (response) {
    //         const category = response["category"];
    //         const probability = parseFloat(response["probability"]).toFixed(2) * 100;
    //         $("#ajp-probability1").html(category + " (" + probability + "%) :");
    //     },
    //     error: function (error) {
    //         console.log("Some error has occured");
    //         console.log(error)
    //     }
    // });
}