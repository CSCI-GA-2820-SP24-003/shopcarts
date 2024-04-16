$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_user_id").val(res.user_id);
        $("#shopcart_name").val(res.name);
        $("#shopcart_total_price").val(res.total_price);
        // if (res.status == "ACTIVE") {
        //     $("#shopcart_status").val("ACTIVE");
        // } else if (res.status == "PENDING")
        //     $("#shopcart_status").val("PENDING");
        //   else {
        //     $("#shopcart_status").val("INACTIVE");
        // }
        $("#shopcart_status").val(res.status);
        //$("#shopcart_items").val(res.items);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_user_id").val("");
        $("#shopcart_name").val("");
        $("#shopcart_total_price").val("");
        $("#shopcart_status").val("");
        //$("#shopcart_items").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let user_id = $("#shopcart_user_id").val();
        let name = $("#shopcart_name").val();
        let total_price = $("#shopcart_total_price").val();
        let status = $("#shopcart_status").val();
        //let items = $("#shopcart_items").val();

        let data = {
            "user_id": user_id,
            "name": name,
            "total_price": total_price,
            "status": status
            //"items": items
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // // ****************************************
    // // Update a Pet
    // // ****************************************

    // $("#update-btn").click(function () {

    //     let pet_id = $("#pet_id").val();
    //     let name = $("#pet_name").val();
    //     let category = $("#pet_category").val();
    //     let available = $("#pet_available").val() == "true";
    //     let gender = $("#pet_gender").val();
    //     let birthday = $("#pet_birthday").val();

    //     let data = {
    //         "name": name,
    //         "category": category,
    //         "available": available,
    //         "gender": gender,
    //         "birthday": birthday
    //     };

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //             type: "PUT",
    //             url: `/pets/${pet_id}`,
    //             contentType: "application/json",
    //             data: JSON.stringify(data)
    //         })

    //     ajax.done(function(res){
    //         update_form_data(res)
    //         flash_message("Success")
    //     });

    //     ajax.fail(function(res){
    //         flash_message(res.responseJSON.message)
    //     });

    // });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // // ****************************************
    // // Delete a Pet
    // // ****************************************

    // $("#delete-btn").click(function () {

    //     let pet_id = $("#pet_id").val();

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //         type: "DELETE",
    //         url: `/pets/${pet_id}`,
    //         contentType: "application/json",
    //         data: '',
    //     })

    //     ajax.done(function(res){
    //         clear_form_data()
    //         flash_message("Pet has been Deleted!")
    //     });

    //     ajax.fail(function(res){
    //         flash_message("Server error!")
    //     });
    // });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Shopcart
    // ****************************************

    $("#search-btn").click(function () {

        let user_id = $("#shopcart_user_id").val();
        let name = $("#shopcart_name").val();
        let total_price = $("#shopcart_total_price").val();
        let status = $("#shopcart_status").val();

        let queryString = ""

        if (user_id) {
            queryString += 'user_id=' + user_id
        }
        if (name) {
            queryString += 'name=' + name
        }
        if (total_price) {
            if (queryString.length > 0) {
                queryString += '&total_price=' + total_price
            } else {
                queryString += 'total_price=' + total_price
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">user_id</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Total_price</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '</tr></thead><tbody>'
            let firstShopcart = "";
            for(let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                table +=  `<tr id="row_${i}"><td>${shopcart.id}</td><td>${shopcart.user_id}</td><td>${shopcart.name}</td><td>${shopcart.total_price}</td><td>${shopcart.status}</td></tr>`;
                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstShopcart != "") {
                update_form_data(firstShopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
