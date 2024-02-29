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
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer,
        db.ForeignKey("shopcart.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(64))  # e.g., work, home, vacation, etc.

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] shopcart[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.name}"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Address from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Address: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained bad or no data "
                + str(error)
            ) from error

        return self
