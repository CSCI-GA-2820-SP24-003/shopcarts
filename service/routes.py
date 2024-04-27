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
# spell: ignore Rofrano jsonify restx dbname shopcart shopcarts reqparse
"""
Shop Cart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shop Carts
"""
from decimal import Decimal
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse  # , inputs
from service.models import ShopCart, ShopCartItem
from service.models.shop_cart import ShopCartStatus
from service.common import status  # HTTP Status Codes
from . import api


#####################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def read_health():
    """Endpoint for health check.
    Returns the health status of the application."""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


# Shopcart Item model
create_item_model = api.model(
    "Item",
    {
        "id": fields.Integer(required=True, description="Id of the shopcart item"),
        "shop_cart_id": fields.Integer(required=True, description="Id of the shopcart"),
        "name": fields.String(required=True, description="Name of the item"),
        "product_id": fields.Integer(required=True, description="Id of the product"),
        "quantity": fields.Integer(required=True, description="Quantity of product"),
        "price": fields.Float(required=True, description="Price of the product"),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The Id of the item assigned internally by the service",
        ),
        "shop_cart_id": fields.Integer(
            readOnly=True,
            description="The Id of the shopcart to which the item belongs",
        ),
    },
)

# Define the Shopcart model
create_shopcart_model = api.model(
    "Shopcart",
    {
        "user_id": fields.Integer(
            required=True, description="User ID of the shopcart owner"
        ),
        "name": fields.String(required=True, description="Name of the shopcart"),
        "total_price": fields.Float(
            required=True, description="Total price of the shopcart"
        ),
        # pylint: disable=protected-access
        "status": fields.String(
            enum=ShopCartStatus._member_names_,
            description="Status of the shopcart",
        ),
        "items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="Items in the shopcart",
        ),
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    create_shopcart_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The Id of the shopcart assigned internally by the service",
        ),
        "items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="Items in the shopcart",
        ),
    },
)

# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "name", type=str, location="args", required=False, help="List Shopcarts by name"
)
shopcart_args.add_argument(
    "status", type=str, location="args", required=False, help="List Shopcarts by status"
)
shopcart_args.add_argument(
    "user_id", type=int, location="args", required=False, help="List Shopcarts by User ID"
)


######################################################################
#  PATH: /shopcarts/{id}
######################################################################
@api.route("/shopcarts/<shopcart_id>")
@api.param("shopcart_id", "The shopcart identifier")
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a single Shopcart
    GET /shopcart{id} - Returns a Shopcart with the id
    PUT /shopcart{id} - Update a Shopcart with the id
    DELETE /shopcart{id} -  Deletes a Shopcart with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart

        This endpoint will return a Shopcart based on it's id
        """
        app.logger.info("Request for Shopcart with id: %s", shopcart_id)

        # See if the account exists and abort if it doesn't
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING SHOPCART
    # ------------------------------------------------------------------
    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.response(400, "The posted shopcart data was not valid")
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
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
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        shopcart.deserialize(data)
        shopcart.id = shopcart_id
        shopcart.update()

        app.logger.info("ShopCart with ID: %d updated.", shopcart.id)
        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
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
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    # ------------------------------------------------------------------
    # LIST ALL SHOPCARTS
    # ------------------------------------------------------------------
    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """List all shop carts"""
        app.logger.info("Request for Shop Cart list")
        shop_carts = []
        args = shopcart_args.parse_args()

        if args.get("user_id"):
            app.logger.info("Filtering by user_id: %s", args.get("user_id"))
            shop_carts = ShopCart.find_by_user_id(args.get("user_id"))
        elif args.get("name"):
            app.logger.info("Filtering by name: %s", args.get("name"))
            shop_carts = ShopCart.find_by_name(args.get("name")).all()
        elif args.get("status"):
            app.logger.info("Filtering by status: %s", args.get("status"))
            shop_carts = ShopCart.find_by_status(args.get("status"))
        else:
            app.logger.info("Returning unfiltered list.")
            shop_carts = ShopCart.all()

        app.logger.info("[%s] shopcarts returned", len(shop_carts))
        results = [shop_cart.serialize() for shop_cart in shop_carts]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW SHOPCART
    # ------------------------------------------------------------------
    @api.doc("create_shopcarts")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Creates a shop cart
        This endpoint will create a shop cart based the data in the body that is posted
        """
        app.logger.info("Request to create an ShopCart")
        check_content_type("application/json")

        # Create the shopcart
        shopcart = ShopCart()
        app.logger.debug("Payload = %s", api.payload)
        shopcart.deserialize(api.payload)
        shopcart.create()

        # Create a message to return
        app.logger.info("shopcart with new id [%s] created!", shopcart.id)
        location_url = api.url_for(ShopcartResource, shopcart_id=shopcart.id, _external=True)

        return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /shopcarts/{shopcart_id}/status
######################################################################
@api.route("/shopcarts/<shopcart_id>/status")
@api.param("shopcart_id", "The shopcart identifier")
class UpdateStatusResource(Resource):
    """update a shopcart status"""

    @api.doc("update_shopcart_status")
    @api.response(404, "Shopcart not found")
    @api.response(409, "The Shopcart is not available")
    def patch(self, shopcart_id):
        """
        Update a ShopCart status

        This endpoint will update a ShopCart's status based the body that is posted
        """
        app.logger.info("Request to update shopcart with id: %d", shopcart_id)
        check_content_type("application/json")

        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with id: '{shopcart_id}' was not found.",
            )

        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        if "status" in data:
            shopcart.status = ShopCartStatus[data["status"]]
            shopcart.update()
        else:
            error(status.HTTP_400_BAD_REQUEST, "status field was not found")

        app.logger.info(
            "ShopCart with ID: %d updated the status %s.", shopcart.id, data["status"]
        )
        return shopcart.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/status/{status_name}
######################################################################
@api.route("/shopcarts/status/<status_name>")
@api.param("shopcart_status", "The shopcart status")
class FindStatusResource(Resource):
    """find shopcarts by status"""

    @api.doc("find_shopcart_by_status")
    @api.response(404, "status not found")
    def get(self, status_name):
        """
        Sort ShopCarts by Status

        This endpoint will return the ShopCarts sorted by the given status
        """
        app.logger.info("Request to sort ShopCarts by Status: %s", status_name)

        # Convert the status string to ShopCartStatus enum
        try:
            status_enum = ShopCartStatus[status_name.upper()]
        except KeyError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid status value: '{status_name}'. Must be one of {[s.name for s in ShopCartStatus]}",
            )

        shopcarts = ShopCart.find_by_status(status_enum)
        results = [shopcart.serialize() for shopcart in shopcarts]

        return results, status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/user/{user_id}
######################################################################
@api.route("/shopcarts/user/<int:user_id>")
@api.param("user_id", "The shopcart user_id")
class UserResource(Resource):
    """find shopcarts by user_id"""

    @api.doc("find_shopcart_by_user_id")
    @api.response(404, "status not found")
    def get(self, user_id):
        """
        Search ShopCarts by User ID

        This endpoint will return the ShopCarts associated with the given user_id
        """
        app.logger.info("Request to search ShopCarts by User ID: %s", user_id)

        shopcarts = ShopCart.find_by_user_id(user_id)
        if not shopcarts:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"No ShopCarts found for User ID '{user_id}'.",
            )

        results = [shopcart.serialize() for shopcart in shopcarts]
        return results, status.HTTP_200_OK


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------
######################################################################
#  PATH: /shopcarts/{shopcart_id}/items/{item_id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """Handles interactions with Shopcart Items"""
    # ------------------------------------------------------------------
    # GET SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("get_shopcart_items")
    @api.response(404, "Shopcart not found")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """
        Get an Item

        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Item %s for ShopCart id: %s", (item_id, shopcart_id)
        )

        # Search for the shopcart
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with ID '{shopcart_id}' could not be found",
            )

        # See if the item exists and abort if it doesn't
        item = ShopCartItem.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_shopcart_items")
    @api.response(204, "Item deleted")
    @api.response(404, "Shopcart not found")
    def delete(self, shopcart_id, item_id):
        """
        Delete shopcart item

        This endpoint will delete a shopcart item
        """
        app.logger.info(
            "Request to delete item %s for a shopcart id: %s", (item_id, shopcart_id)
        )

        # Search for the shopcart
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with ID '{shopcart_id}' could not be found",
            )

        item = ShopCartItem.find(item_id)
        if item:
            item.delete()

            # update the total price
            shopcart.update_total_price()

        return "", status.HTTP_204_NO_CONTENT

    # ------------------------------------------------------------------
    # UPDATE SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("update_shopcart_item")
    @api.response(404, "Shopcart not found")
    @api.response(404, "Item not found")
    @api.response(400, "The Item data was not valid")
    @api.response(415, "Invalid header content-type")
    @api.expect(item_model)
    def put(self, shopcart_id, item_id):
        """
        Update an Item

        This endpoint will update an Item based the body that is posted
        """
        app.logger.info(
            "Request to update Item %s for Shopcart id: %s", (item_id, shopcart_id)
        )
        check_content_type("application/json")

        # Search for the shopcart
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with ID '{shopcart_id}' could not be found",
            )

        # See if the address exists and abort if it doesn't
        item = ShopCartItem.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{item_id}' could not be found.",
            )

        # Update from the json in the body of the request
        item.deserialize(api.payload)
        item.id = item_id
        item.update()

        # update the total price
        shopcart.update_total_price()

        return item.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/{shopcart_id}/items
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """Handles interactions with collections of Shopcart Items"""
    # ------------------------------------------------------------------
    # CREATE SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("create_shopcart_item")
    @api.response(400, "Invalid shopcart item request body")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(item_model, code=201)
    def post(self, shopcart_id):
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
        item.deserialize(api.payload)

        # Append item to the shopcart
        # if the item does exists in the shopcart
        # change the item quantity by adding one
        item_orig = ShopCartItem.find_by_name(item.name)
        if item_orig:
            item_orig.quantity = item_orig.quantity + item.quantity
            item_orig.update()
            item = item_orig

        # if the item does not exist in the shopcart
        # add a new item
        else:
            shopcart.items.append(item)
            shopcart.update()

        # update the total price
        shopcart.update_total_price()

        # Create a message to return
        location_url = api.url_for(
            ItemResource, shopcart_id=shopcart.id, item_id=item.id, _external=True
        )

        return (
            item.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )

    # ------------------------------------------------------------------
    # LIST SHOPCART ITEMS
    # ------------------------------------------------------------------
    @api.doc("list_shopcart_items")
    @api.response(404, "Shopcart not found")
    @api.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """
        List all Items in a ShopCart

        This endpoint returns all items within a specified shopcart.
        """
        app.logger.info("Request to list items for ShopCart id: %s", shopcart_id)

        # Attempting to find the shopcart first to verify it exists
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with id '{shopcart_id}' could not be found.",
            )

        # Getting query parameters
        name = request.args.get("name")
        min_price = request.args.get("min_price")
        max_price = request.args.get("max_price")

        # pylint: disable=too-many-boolean-expressions
        filtered_items = []
        for item in shopcart.items:
            if (
                (not name or item.name == name)
                and (not min_price or item.price >= Decimal(min_price))
                and (not max_price or item.price <= Decimal(max_price))
            ):
                filtered_items.append(item)

        # items = ShopCartItem.find_by_shopcart_id(shopcart_id)
        if not filtered_items:
            return [], status.HTTP_200_OK

        results = [item.serialize() for item in filtered_items]
        app.logger.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/{shopcart_id}/products/{product_id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/products/<int:product_id>", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """Handles interactions with Product Items"""
    # ------------------------------------------------------------------
    # GET SHOPCART ITEM by PRODUCT ID
    # ------------------------------------------------------------------
    @api.doc("get_shopcart_items_by_product_id")
    @api.response(404, "Shopcart not found")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, product_id):
        """
        Get an Item

        This endpoint returns just an item using the product id
        """
        app.logger.info(
            "Request to retrieve Item %s for ShopCart id: %s", (product_id, shopcart_id)
        )

        # Search for the shopcart
        shopcart = ShopCart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"ShopCart with ID '{shopcart_id}' could not be found",
            )

        # See if the item exists and abort if it doesn't
        item = ShopCartItem.find_by_product_id(product_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK


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
