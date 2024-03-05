"""
Test cases for ShopCart Model
"""

import os
import logging
from unittest import TestCase

# from unittest.mock import patch
from wsgi import app
from service.models import (
    db,
    DataValidationError,
    ShopCart,
    ShopCartItem,
)
from tests.factories import ShopCartFactory, ShopCartItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  S H O P  C A R T  I T E M  T E S T   C A S E S
######################################################################
class TestShopCartItem(TestCase):
    """Shop Cart Item Model CRUD Tests"""

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
    def test_add_shop_cart_with_item(self):
        """It should create and add a Shop Cart to the database with an item"""
        shop_carts = ShopCart.all()
        self.assertEqual(shop_carts, [])
        shop_cart = ShopCartFactory()
        shop_cart_item = ShopCartItemFactory(shop_cart=shop_cart)
        shop_cart.items.append(shop_cart_item)
        shop_cart.create()

        self.assertIsNotNone(shop_cart.id)
        shop_carts = ShopCart.all()
        self.assertEqual(len(shop_carts), 1)
        added_shop_cart = ShopCart.find(shop_cart.id)
        self.assertEqual(added_shop_cart.items[0].quantity, shop_cart_item.quantity)

    # def test_read_shop_cart_item(self):
    #     """It should read a single Shop Cart Item from the database"""
    #     shop_cart_item = ShopCartItemFactory()
    #     logging.debug(shop_cart_item)
    #     shop_cart_item.id = None
    #     shop_cart_item.create()
    #     self.assertIsNotNone(shop_cart_item.id)
    #     # Find Shop Cart Item By id
    #     found_shop_cart_item = ShopCartItem.find(shop_cart_item.id)
    #     self.assertEqual(found_shop_cart_item.id, shop_cart_item.id)
    #     self.assertEqual(found_shop_cart_item.quantity, shop_cart_item.quantity)

    def test_update_shop_cart_item(self):
        """It should update a Shop Cart Item"""
        shop_cart_item = ShopCartItemFactory()
        logging.debug(shop_cart_item)
        shop_cart_item.id = None
        shop_cart_item.create()
        logging.debug(shop_cart_item)
        self.assertIsNotNone(shop_cart_item.id)
        # Update shop cart item
        shop_cart_item.quantity = 10
        shop_cart_item.update()
        self.assertEqual(shop_cart_item.quantity, 10)
        shop_cart_items = ShopCartItem.all()
        self.assertEqual(len(shop_cart_items), 1)
        self.assertEqual(shop_cart_items[0].id, shop_cart_item.id)
        self.assertEqual(shop_cart_items[0].quantity, 10)

    # def test_delete_shop_cart_with_item(self):
    #     """It should delete a Shop Cart with an item"""
    #     shop_carts = ShopCart.all()
    #     self.assertEqual(shop_carts, [])

    #     shop_cart = ShopCartFactory()
    #     shop_cart_item = ShopCartItemFactory(shop_cart=shop_cart)
    #     shop_cart.create()

    #     self.assertIsNotNone(shop_cart.id)
    #     shop_carts = ShopCart.all()
    #     self.assertEqual(len(shop_carts), 1)

    #     shop_cart = ShopCart.find(shop_cart.id)
    #     shop_cart_item = shop_cart.items[0]
    #     shop_cart_item.delete()
    #     shop_cart.update()

    #     shop_cart = ShopCart.find(shop_cart.id)
    #     self.assertEqual(len(shop_cart.items), 0)

    # def test_list_all_shop_cart_items(self):
    #     """It should list all Shop Cart Items in the database"""
    #     shop_cart_items = ShopCartItem.all()
    #     self.assertEqual(shop_cart_items, [])

    #     for _ in range(10):
    #         shop_cart_item = ShopCartItemFactory()
    #         shop_cart_item.create()

    #     shop_cart_items = ShopCartItem.all()
    #     self.assertEqual(len(shop_cart_items), 10)

    # def test_serialize_shop_cart_item(self):
    #     """It should serialize a Shop Cart Item"""
    #     shop_cart_item = ShopCartItemFactory()
    #     data = shop_cart_item.serialize()
    #     self.assertNotEqual(data, None)
    #     self.assertEqual(data["id"], shop_cart_item.id)
    #     self.assertEqual(data["product_id"], shop_cart_item.product_id)
    #     self.assertEqual(data["shop_cart_id"], shop_cart_item.shop_cart_id)
    #     self.assertEqual(data["quantity"], shop_cart_item.quantity)
    #     self.assertEqual(data["price"], shop_cart_item.price)

    # def test_deserialize_shop_cart_item(self):
    #     """It should deserialize a Shop Cart Item"""
    #     data = ShopCartItemFactory()
    #     data.create()
    #     shop_cart_item = ShopCartItem()
    #     shop_cart_item.deserialize(data.serialize())
    #     self.assertNotEqual(shop_cart_item, None)
    #     self.assertEqual(shop_cart_item.shop_cart_id, data.shop_cart_id)
    #     self.assertEqual(shop_cart_item.product_id, data.product_id)
    #     self.assertEqual(shop_cart_item.quantity, data.quantity)
    #     self.assertEqual(shop_cart_item.price, data.price)

    # # # + + + + + + + + + + + + + SAD PATHS + + + + + + + + + + + + + + +
    # def test_deserialize_missing_data(self):
    #     """It should not deserialize a Shop Cart Item with missing data"""
    #     data = {"id": 42, "quantity": 5}
    #     sci = ShopCartItem()
    #     self.assertRaises(DataValidationError, sci.deserialize, data)

    # def test_deserialize_bad_data(self):
    #     """It should not deserialize a Shop Cart Item with bad data"""
    #     data = ""
    #     sci = ShopCartItem()
    #     self.assertRaises(DataValidationError, sci.deserialize, data)
