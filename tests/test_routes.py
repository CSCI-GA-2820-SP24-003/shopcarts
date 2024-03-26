"""
Shop Cart API Service Test Suite
"""

import os
import logging
from decimal import Decimal
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, ShopCart
from .factories import ShopCartFactory, ShopCartItemFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"
MAX_NUM = 99999


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopCartService(TestCase):
    """REST API Server Tests"""

    # pylint: disable=duplicate-code
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
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        print(updated_shopcart)

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

    def test_get_shopcart_update_fail(self):
        """It should raise shopcart not found sign"""
        # get the id of a shopcart
        shopcart = ShopCartFactory()
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"ShopCart with id: '{shopcart.id}' was not found.",
            resp.data.decode(),
        )

    # ---------------------------------------------------------------------
    #                I T E M   M E T H O D S
    # ---------------------------------------------------------------------

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

    def test_get_shopcart_item_when_no_shopcart(self):
        """It should Get an error when a shopcart id does not exist"""
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
            f"{BASE_URL}/{shopcart.id + MAX_NUM}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_shopcart_item(self):
        """It should delete a shopcart item"""
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

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_shopcart_item_when_no_shopcart(self):
        """It should Get an error when a shopcart id does not exist"""
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

        # try to delete an non-exist shopcart
        resp = self.client.delete(
            f"{BASE_URL}/{shopcart.id + MAX_NUM}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_item(self):
        """It should Update an item on a shopcart"""
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
        data["quantity"] = 3

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["shop_cart_id"], shopcart.id)
        self.assertEqual(data["quantity"], 3)

    def test_update_shopcart_item_when_no_shopcart(self):
        """It should Get an error when a shopcart id does not exist"""
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
        data["quantity"] = 3

        # try send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id + MAX_NUM}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shopcart_items(self):
        """It should List all items in a shopcart"""
        # Create a shopcart and add multiple items
        shopcart = self._create_shopcarts(1)[0]
        num_items = 3
        created_items = []

        for _ in range(num_items):
            item = ShopCartItemFactory()
            resp = self.client.post(
                f"{BASE_URL}/{shopcart.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            created_items.append(resp.get_json())

        # Retrieve all items in the shopcart
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        # Assertions for each item's fields
        self.assertEqual(len(data), num_items)
        for item_data in data:
            self.assertTrue(
                any(item_data["name"] == item["name"] for item in created_items)
            )
            self.assertTrue(
                any(
                    item_data["product_id"] == item["product_id"]
                    for item in created_items
                )
            )
            self.assertTrue(
                any(item_data["quantity"] == item["quantity"] for item in created_items)
            )
            self.assertTrue(
                any(
                    str(item_data["price"]) == str(item["price"])
                    for item in created_items
                )
            )

    def test_create_shopcart_item_fail(self):
        """It should raise shopcart not found sign"""

        shopcart = ShopCartFactory()
        item = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"ShopCart with ID '{shopcart.id}' could not be found",
            resp.data.decode(),
        )

    def test_update_shopcart_item_fail(self):
        """It should raise shopcart item not found sign"""
        shopcart = self._create_shopcarts(1)[0]
        item = ShopCartItemFactory()
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item.id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{item.id}' could not be found.",
            resp.data.decode(),
        )

    def test_list_shopcart_item_with_no_shopcart(self):
        """It should raise shopcart not found sign"""
        shopcart = ShopCartFactory()
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"ShopCart with id '{shopcart.id}' could not be found.",
            resp.data.decode(),
        )

    def test_list_shopcart_item_with_no_item(self):
        """It should raise no items not found sign"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), [])

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        shopcart = ShopCartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shopcart_total_price_with_new_item(self):
        """
        It should update the shopcart total price
        once a new item is added
        """
        shop_cart = self._create_shopcarts(1)[0]
        item_1 = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=item_1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        item_2 = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=item_2.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get(
            f"{BASE_URL}/{shop_cart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(
            data["total_price"],
            str(item_1.price * item_1.quantity + item_2.price * item_2.quantity),
        )

    def test_shopcart_total_price_with_delete_item(self):
        """
        It should update the shopcart total price
        once an item is deleted
        """
        shopcart = self._create_shopcarts(1)[0]
        # add the first item
        item = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        item_id = data["id"]

        # add the second item
        item_2 = ShopCartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item_2.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # send delete request to delete the first item
        resp = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # the total price should equal to the second item's total price
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["total_price"], str(item_2.price * item_2.quantity))

    def test_shopcart_total_price_with_update_item(self):
        """
        It should update the shopcart total price
        once an item is updated
        """
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
        data["quantity"] = 3

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # check total price
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["total_price"], str(item.price * 3))
