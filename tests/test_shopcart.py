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
Test cases for Shopcart Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Shopcart, Item, DataValidationError, db
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcart(TestCase):
    """Shopcart Model Test Cases"""

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
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """It should Create a shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        # print("fake_shopcart id" + str(fake_shopcart.id))
        # print("fake_shopcart name" + fake_shopcart.name)
        # pylint: disable=unexpected-keyword-arg
        shopcart = Shopcart()
        shopcart.deserialize({"id": str(fake_shopcart.id), "name": fake_shopcart.name})
        self.assertIsNotNone(shopcart)
        self.assertIsNotNone(shopcart.id)
        self.assertEqual(shopcart.name, fake_shopcart.name)
