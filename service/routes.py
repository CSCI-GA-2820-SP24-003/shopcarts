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
from service.models import ShopCart
from service.common import status  # HTTP Status Codes


#####################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # To do when list accounts available
            # paths=url_for("list_accounts", _external=True),
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

    # Create the account
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    # To do when list shopcarts is done
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  L I S T  S H O P C A R T S  E N D P O I N T
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """List all shop carts"""
    app.logger.info("Request for Shop Cart list")
    shop_carts = ShopCart.all()

    results = [shop_cart.serialize() for shop_cart in shop_carts]

    return jsonify(results), status.HTTP_200_OK


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
