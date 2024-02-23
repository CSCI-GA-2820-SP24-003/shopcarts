"""
TestYourResourceModel API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, ShopCart
import factory
import json

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopCartService(TestCase):
    """ REST API Server Tests """

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
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...
    def test_create_shopcart(self):
        """It should create a ShopCart"""
        #user_id = factory.Sequence(lambda n: 100)
        #name = factory.Sequence(lambda n: 1000)
        new_cart = {"id": "5", "name": "6"}
        #check if create successfully
        response = self.client.post("/shopcarts", json=new_cart)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        #check if data is correct 
        res_cart = response.get_json()
        self.assertEqual(res_cart["name"], new_cart["name"])
        #self.assertEqual(res_cart["id"], new_cart.id)
        
        