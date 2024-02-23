"""
Test cases for ShopCart Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import ShopCart, ShopCartStatus, db
from tests.factories import ShopCartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  ShopCart        M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopCartModel(TestCase):
    """Test Cases for ShopCart Model"""

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
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

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
        self.assertEqual(found_shop_cart.id, shop_cart.id)
        self.assertEqual(found_shop_cart.user_id, shop_cart.user_id)

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

    # def test_update_no_id(self):
    #     """It should not update a Shop Cart"""
    #     shop_cart = ShopCartFactory()
    #     logging.debug(shop_cart)
    #     shop_cart.id = None
    #     self.assertRaises(DataValidationError, shop_cart.update)
