######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shop Cart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shop Carts
"""

from flask import jsonify, request, url_for, abort  # , request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import ShopCart, ShopCartItem
from service.common import status  # HTTP Status Codes


#####################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Shopcart REST API Service",
            version="1.0",
            # To do when list Shopcart available
            # paths=url_for("list_Shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a shop cart
    This endpoint will create a shop cart based the data in the body that is posted
    """
    app.logger.info("Request to create an ShopCart")
    check_content_type("application/json")

    # Create the shopcart
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    # To do when list shopcarts is done
    # location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)
    location_url = "/"

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """List all shop carts"""
    app.logger.info("Request for Shop Cart list")
    shop_carts = []

    name = request.args.get("name")
    if name:
        shop_carts = ShopCart.find_by_name(name)
    else:
        shop_carts = ShopCart.all()

    results = [shop_cart.serialize() for shop_cart in shop_carts]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %d", shopcart_id)

    shopcart = ShopCart.find(shopcart_id)
    if shopcart:
        shopcart.delete()

    app.logger.info("Shopcart with ID: %d delete complete.", shopcart_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE AN EXISTING ShopCart
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a ShopCart

    This endpoint will update a ShopCart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id: %d", shopcart_id)
    check_content_type("application/json")

    shopcart = ShopCart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"ShopCart with id: '{shopcart_id}' was not found.",
        )

    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    app.logger.info("ShopCart with ID: %d updated.", shopcart.id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# CREATE A NEW SHOPCART ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_shopcart_item(shopcart_id):
    """
    Creates a shop cart item
    This endpoint will create a shop cart item and add it to the shopcart
    """
    app.logger.info("Request to create an Item for ShopCart with ID: %s", shopcart_id)
    check_content_type("application/json")

    # Search for the shopcart
    shopcart = ShopCart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"ShopCart with ID '{shopcart_id}' could not be found",
        )

    # Create item from json data
    item = ShopCartItem()
    item.deserialize(request.get_json())

    # Append item to the shopcart
    shopcart.items.append(item)
    shopcart.update()

    # Create a message to return
    message = item.serialize()

    return jsonify(message), status.HTTP_201_CREATED


######################################################################
# RETRIEVE AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_shopcart_items(shopcart_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve Item %s for ShopCart id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and abort if it doesn't
    item = ShopCartItem.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
