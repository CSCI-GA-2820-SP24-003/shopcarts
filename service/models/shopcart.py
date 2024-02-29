"""
Models for ShopCarts Service

All of the models are stored in this module
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")

##################################################
# SHOPCART MODEL
##################################################


class Shopcart(db.Model, PersistentBase):
    """
    Class that represents a shopcart
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    items = db.relationship("Item", backref="shopcart", passive_deletes=True)

    # Todo: Place the rest of your schema here...
    def __repr__(self):
        return f"<Shopcart {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a ShopCart into a dictionary"""
        shopcart = {"id": self.id, "name": self.name, "items": []}
        for item in self.items:
            shopcart["items"].append(item.serialize())

        return shopcart

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopCart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_name(cls, name):
        """Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCarts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
