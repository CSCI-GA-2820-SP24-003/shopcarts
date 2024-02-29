"""
Test cases for ShopCart Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import (
    db,
    DataValidationError,
    ShopCart,
    ShopCartStatus,
    ShopCartItem,
)
from tests.factories import ShopCartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  M O D E L S  T E S T   C A S E S
######################################################################
class TestShopCart(TestCase):
    """Shop Cart Model CRUD Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(ShopCart).delete()  # clean up the last tests
        db.session.query(ShopCartItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    # + + + + + + + + + + + + + HAPPY PATHS + + + + + + + + + + + + + + +
    def test_create_a_shop_cart(self):
        """It should create a Shop Cart and assert that it exists"""
        shop_cart = ShopCart(
            user_id=1, name="sc-2801", total_price=25.25, status=ShopCartStatus.ACTIVE
        )
        self.assertEqual(str(shop_cart), "<ShopCart sc-2801 id=[None]>")
        self.assertTrue(shop_cart is not None)
        self.assertEqual(shop_cart.user_id, 1)
        self.assertEqual(shop_cart.name, "sc-2801")
        self.assertEqual(shop_cart.total_price, 25.25)
        self.assertEqual(shop_cart.status, ShopCartStatus.ACTIVE)

    def test_add_shop_cart(self):
        """It should create and add a Shop Cart to the database"""
        shop_carts = ShopCart.all()
        self.assertEqual(shop_carts, [])
        shop_cart = ShopCart(
            user_id=1, name="sc-2801", total_price=25.25, status=ShopCartStatus.ACTIVE
        )
        self.assertTrue(shop_cart is not None)
        self.assertEqual(shop_cart.id, None)
        shop_cart.create()
        self.assertIsNotNone(shop_cart.id)
        shop_carts = ShopCart.all()
        self.assertEqual(len(shop_carts), 1)

    def test_read_shop_cart(self):
        """It should read a single Shop Cart from the database"""
        shop_cart = ShopCartFactory()
        logging.debug(shop_cart)
        shop_cart.id = None
        shop_cart.create()
        self.assertIsNotNone(shop_cart.id)
        # Find Shop Cart By id
        found_shop_cart = ShopCart.find(shop_cart.id)
        print(found_shop_cart)
        self.assertEqual(found_shop_cart.id, shop_cart.id)
        self.assertEqual(found_shop_cart.user_id, shop_cart.user_id)
        self.assertEqual(found_shop_cart.items, [])

    def test_update_shop_cart(self):
        """It should update a Shop Cart"""
        shop_cart = ShopCartFactory()
        logging.debug(shop_cart)
        shop_cart.id = None
        shop_cart.create()
        logging.debug(shop_cart)
        self.assertIsNotNone(shop_cart.id)
        # Update shop cart
        shop_cart.total_price = 250.00
        shop_cart.update()
        self.assertEqual(shop_cart.total_price, 250.00)
        shop_carts = ShopCart.all()
        self.assertEqual(len(shop_carts), 1)
        self.assertEqual(shop_carts[0].id, shop_cart.id)
        self.assertEqual(shop_carts[0].total_price, 250.00)

    def test_delete_shop_cart(self):
        """It should delete a Shop Cart"""
        shop_cart = ShopCartFactory()
        shop_cart.create()
        self.assertEqual(len(ShopCart.all()), 1)
        shop_cart.delete()
        self.assertEqual(len(ShopCart.all()), 0)

    def test_list_all_shop_carts(self):
        """It should list all Shop Carts in the database"""
        shop_carts = ShopCart.all()
        self.assertEqual(shop_carts, [])

        for _ in range(7):
            shop_cart = ShopCartFactory()
            shop_cart.create()

        shop_carts = ShopCart.all()
        self.assertEqual(len(shop_carts), 7)

    def test_serialize_shop_cart(self):
        """It should serialize a Shop Cart"""
        shop_cart = ShopCartFactory()
        shop_cart_item = ShopCartItem()
        shop_cart.items.append(shop_cart_item)
        data = shop_cart.serialize()
        self.assertNotEqual(data, None)
        self.assertEqual(data["id"], shop_cart.id)
        self.assertEqual(data["user_id"], shop_cart.user_id)
        self.assertEqual(data["name"], shop_cart.name)
        self.assertEqual(data["total_price"], shop_cart.total_price)
        self.assertEqual(data["status"], shop_cart.status.name)
        self.assertEqual(len(data["items"]), 1)
        items = data["items"]
        self.assertEqual(items[0]["id"], shop_cart_item.id)
        self.assertEqual(items[0]["product_id"], shop_cart_item.product_id)
        self.assertEqual(items[0]["shop_cart_id"], shop_cart_item.shop_cart_id)
        self.assertEqual(items[0]["quantity"], shop_cart_item.quantity)
        self.assertEqual(items[0]["price"], shop_cart_item.price)

    def test_deserialize_shop_cart(self):
        """It should deserialize a Shop Cart"""
        data = ShopCartFactory().serialize()
        shop_cart = ShopCart()
        shop_cart.deserialize(data)
        self.assertNotEqual(shop_cart, None)
        self.assertEqual(shop_cart.id, None)
        self.assertEqual(shop_cart.user_id, data["user_id"])
        self.assertEqual(shop_cart.name, data["name"])
        self.assertEqual(shop_cart.total_price, data["total_price"])
        self.assertEqual(shop_cart.status.name, data["status"])

    # + + + + + + + + + + + + + SAD PATHS + + + + + + + + + + + + + + +
    def test_update_no_id(self):
        """It should not update a Shop Cart"""
        shop_cart = ShopCartFactory()
        logging.debug(shop_cart)
        shop_cart.id = None
        self.assertRaises(DataValidationError, shop_cart.update)

    def test_deserialize_missing_data(self):
        """It should not deserialize a ShopCart with missing data"""
        data = {"id": 42, "name": "sc-42", "total_price": 25.25, "status": "PENDING"}
        sc = ShopCart()
        self.assertRaises(DataValidationError, sc.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize a Shop Cart with bad data"""
        data = ""
        sc = ShopCart()
        self.assertRaises(DataValidationError, sc.deserialize, data)

    def test_deserialize_bad_attribute(self):
        """It should not deserialize a Shop Cart with bad attribute"""
        shop_cart = ShopCartFactory()
        data = shop_cart.serialize()
        data["status"] = "pasta"
        sc = ShopCart()
        self.assertRaises(DataValidationError, sc.deserialize, data)


######################################################################
#  Q U E R Y  T E S T   C A S E S
######################################################################
class TestModelQueries(TestCase):
    """Shop Cart Model Query Tests"""

    def test_find_by_name(self):
        """It should find a Shop Cart by name"""
        shop_carts = ShopCartFactory.create_batch(17)
        for shop_cart in shop_carts:
            shop_cart.create()
        name = shop_carts[10].name
        found = ShopCart.find_by_name(name)
        for sc in found:
            self.assertEqual(sc.name, name)


######################################################################
#  E X C E P T I O N S  T E S T   C A S E S
######################################################################
class TestExceptionHandlers(TestCase):
    """Shop Cart Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        shop_cart = ShopCartFactory()
        self.assertRaises(DataValidationError, shop_cart.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        shop_cart = ShopCartFactory()
        self.assertRaises(DataValidationError, shop_cart.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        shop_cart = ShopCartFactory()
        self.assertRaises(DataValidationError, shop_cart.delete)