"""
Shop Cart API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, ShopCart
from .factories import ShopCartFactory, ShopCartItemFactory
from decimal import Decimal

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopCartService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(ShopCart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   F U N C T I O N S
    ######################################################################

    def _create_shopcarts(self, batch_size):
        """Factory method to create shop carts in bulk"""
        shop_carts = []
        for _ in range(batch_size):
            shop_cart = ShopCartFactory()
            resp = self.client.post(BASE_URL, json=shop_cart.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shop cart",
            )
            new_shop_cart = resp.get_json()
            shop_cart.id = new_shop_cart["id"]
            shop_carts.append(shop_cart)

        return shop_carts

    ######################################################################
    #  S H O P   C A R T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_shopcart(self):
        """It should Create a new shop cart"""
        shopcart = ShopCartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["user_id"], shopcart.user_id, "user_id does not match"
        )
        self.assertEqual(new_shopcart["name"], shopcart.name, "name does not match")
        self.assertEqual(
            new_shopcart["total_price"],
            str(shopcart.total_price),
            "total_price does not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Name does not match")
        self.assertEqual(
            new_shopcart["user_id"], shopcart.user_id, "user_id does not match"
        )
        self.assertEqual(
            new_shopcart["total_price"],
            str(shopcart.total_price),
            "total_price does not match",
        )
        self.assertEqual(new_shopcart["items"], shopcart.items, "items does not match")

    def test_get_shopcart_by_name(self):
        """It should Get a shopcart by Name"""
        shopcarts = self._create_shopcarts(3)
        resp = self.client.get(BASE_URL, query_string=f"name={shopcarts[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], shopcarts[1].name)

    def test_get_shopcart(self):
        """It should Read a single shopcart"""
        # get the id of a shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], shopcart.name)

    def test_get_shopcart_not_found(self):
        """It should not Read a shopcart that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shopcarts(self):
        """It should get a list of shop carts"""
        self._create_shopcarts(10)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 10)

    def test_delete_shopcart(self):
        """It should Delete a Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        # TODO: uncomment when get_shopcarts is implemented
        # response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart(self):
        """It should Update an existing ShopCart with all fields"""
        # Create a shopcart to update
        test_shopcart = ShopCartFactory()
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Prepare update payload with modifications to all fields
        new_shopcart = response.get_json()
        update_payload = {
            "user_id": new_shopcart[
                "user_id"
            ],  # Assuming user_id can be updated or is needed for identification
            "name": "Updated Name",
            "total_price": Decimal(new_shopcart["total_price"])
            + 100,  # Example of updating the price
            # Include updates to other fields here
        }

        # Update the shopcart
        response = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}", json=update_payload
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_shopcart = response.get_json()

        # Verify that all fields have been updated correctly
        self.assertEqual(updated_shopcart["name"], update_payload["name"])
        self.assertEqual(
            updated_shopcart["total_price"], str(update_payload["total_price"])
        )
        # Add assertions for other fields here

        print(updated_shopcart)  # For debugging

    def test_update_shop_cart_with_invalid_fields(self):
        """It should not update a shopcart with invalid fields and maintain required fields"""
        # Assuming ShopCartFactory sets a user_id, name, and total_price
        test_shopcart = ShopCartFactory()
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_shopcart = response.get_json()
        update_payload = {
            "user_id": new_shopcart["user_id"],
            "name": "Updated Name",
            "total_price": new_shopcart["total_price"],
            "non_existent_field": "test",
        }

        # Attempt to update the shopcart
        response = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}", json=update_payload
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Fetch the updated shopcart and verify the update
        updated_shopcart = self.client.get(
            f"{BASE_URL}/{new_shopcart['id']}"
        ).get_json()
        # self.assertEqual(updated_shopcart["name"], updated_payload["name"])
        # Ensure non-existent fields are not added
        self.assertNotIn("non_existent_field", updated_shopcart)

    def test_create_shopcart_item(self):
        """It should add an item to a shop cart"""
        shop_cart = self._create_shopcarts(1)[0]
        item = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["shop_cart_id"], shop_cart.id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], str(item.price))

    def test_get_shopcart_item(self):
        """It should Get an item from a shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shop_cart_id"], shopcart.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], str(item.price))
