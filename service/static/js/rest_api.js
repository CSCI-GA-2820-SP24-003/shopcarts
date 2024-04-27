$(function () {

    let SHOPCART_SERVICE_BASE_URL = "/api/shopcarts";

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_user_id").val(res.user_id);
        $("#shopcart_name").val(res.name);
        $("#shopcart_total_price").val(res.total_price);
        $("#shopcart_status").val(res.status);
        //$("#shopcart_items").val(res.items);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_user_id").val("");
        $("#shopcart_name").val("");
        $("#shopcart_total_price").val("");
        $("#shopcart_status").val("");
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
            url: SHOPCART_SERVICE_BASE_URL,
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
    // // Update a Shopcart
    // // ****************************************

    $("#update-btn").click(function () { 

        let shopcart_id = $("#shopcart_id").val();
        let user_id = $("#shopcart_user_id").val();
        let name = $("#shopcart_name").val();
        let total_price = $("#shopcart_total_price").val();
        let status = $("#shopcart_status").val();

        let data = {
            "user_id": user_id,
            "name": name,
            "total_price": total_price,
            "status": status
            //"items": items
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${SHOPCART_SERVICE_BASE_URL}/${shopcart_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
    
    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${SHOPCART_SERVICE_BASE_URL}/${shopcart_id}`,
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

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${SHOPCART_SERVICE_BASE_URL}/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

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
    $("#search-btn").on("click", function() {
        let queryParams = "";
        const user_id = $("#shopcart_user_id").val();
        const name = $("#shopcart_name").val();
        const total_price = $("#shopcart_total_price").val();
        const status = $("#shopcart_status").val();
    
        if (user_id) queryParams += `user_id=${user_id}&`;
        if (name) queryParams += `name=${name}&`;
        if (total_price) queryParams += `total_price=${total_price}&`;
        if (status) queryParams += `status=${status}&`;
    
        queryParams = queryParams.slice(0, -1); // Remove the trailing &
    
        $("#flash_message").empty();
    
        $.ajax({
            type: "GET",
            url: `${SHOPCART_SERVICE_BASE_URL}?${queryString}`,
            contentType: "application/json",
            data: ""
        })
        .done(function(response) {
            $("#search_results").empty();
            const table = $("<table>", { class: "table table-striped", cellpadding: 10 });
            const thead = $("<thead>").appendTo(table);
            $("<tr>").appendTo(thead)
                .append($("<th>", { class: "col-md-2", text: "ID" }))
                .append($("<th>", { class: "col-md-2", text: "User ID" }))
                .append($("<th>", { class: "col-md-2", text: "Name" }))
                .append($("<th>", { class: "col-md-2", text: "Total Price" }))
                .append($("<th>", { class: "col-md-2", text: "Status" }));
    
            const tbody = $("<tbody>").appendTo(table);
            let firstOrder = null;
    
            $.each(response, function(i, order) {
                const row = $("<tr>", { id: `row_${i}` }).appendTo(tbody);
                $("<td>").text(order.id).appendTo(row);
                $("<td>").text(order.user_id).appendTo(row);
                $("<td>").text(order.name).appendTo(row);
                $("<td>").text(order.total_price).appendTo(row);
                $("<td>").text(order.status).appendTo(row);
    
                if (i === 0) firstOrder = order;
            });
    
            $("#search_results").append(table);
    
            if (firstOrder !== null) updateFormData(firstOrder);
    
            flashMessage("Success");
        })
        .fail(function(error) {
            flashMessage(error.responseJSON.message);
        });
    });
    
    function updateFormData(order) {
        $("#shopcart_id").val(order.id);
        $("#shopcart_user_id").val(order.user_id);
        $("#shopcart_name").val(order.name);
        $("#shopcart_total_price").val(order.total_price);
        $("#shopcart_status").val(order.status);
    }
    
    function flashMessage(message) {
        $("#flash_message").text(message);
    }

})
