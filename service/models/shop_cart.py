"""
Shop Cart Model

"""

# from enum import Enum
from .persistent_base import db, logger, DataValidationError, PersistentBase
from .shop_cart_item import ShopCartItem

# from decimal import Decimal


# class ShopCartStatus(Enum):
#     """Enumeration of different shop cart statuses"""

#     # An item has been added to the shop cart
#     ACTIVE = 0
#     # User reached last step of checkout
#     PENDING = 1
#     # Order was fulfilled or cart was abandoned
#     INACTIVE = 3


class ShopCart(db.Model, PersistentBase):
    """
    Class that represents a ShopCart
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(63))
    total_price = db.Column(db.Numeric(precision=10, scale=2))
    # status = db.Column(
    #     db.Enum(
    #         ShopCartStatus, nullable=False, server_default=(ShopCartStatus.ACTIVE.name)
    #     )
    # )
    items = db.relationship("ShopCartItem", backref="shop_cart", passive_deletes=True)

    def __repr__(self):
        return f"<ShopCart {self.name} id=[{self.id}]>"

    def serialize(self) -> dict:
        """Serializes a ShopCart into a dictionary"""
        shop_cart = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "total_price": self.total_price,
            # "status": self.status.name,
            "items": [],
        }
        for item in self.items:
            shop_cart["items"].append(item.serialize())
        return shop_cart

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.user_id = data["user_id"]
            self.name = data["name"]
            self.total_price = data["total_price"]
            # self.status = getattr(ShopCartStatus, data["status"])
            item_list = data.get("items")
            if item_list:
                for json_item in item_list:
                    item = ShopCartItem()
                    item.deserialize(json_item)
                    self.items.append(item)
        # pylint: disable=duplicate-code
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

    def update_total_price(self):
        """
        update the total price of a ShopCart
        """
        price = 0
        for item in self.items:
            if item.price is not None and item.quantity is not None:
                price += item.price * item.quantity

        self.total_price = price
        self.update()

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the ShopCarts in the database"""
        logger.info("Processing all ShopCarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a ShopCart by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCart you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
