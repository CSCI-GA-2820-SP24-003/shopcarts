"""
Shop Cart Item Model

"""

from .persistent_base import db, logger, DataValidationError, PersistentBase


class ShopCartItem(db.Model, PersistentBase):
    """
    Class that represents a ShopCart Item
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    shop_cart_id = db.Column(
        db.Integer, db.ForeignKey("shop_cart.id", ondelete="CASCADE"), nullable=False
    )
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(precision=10, scale=2))

    def __repr__(self):
        return f"<ShopCartItem id=[{self.id}] shop_cart_id=[{self.shop_cart_id}]>"

    def serialize(self) -> dict:
        """Serializes a ShopCart Item into a dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "shop_cart_id": self.shop_cart_id,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data):
        """
        Deserializes a ShopCart Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.shop_cart_id = data["shop_cart_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
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
    def all(cls):
        """Returns all of the ShopCart Items in the database"""
        logger.info("Processing all ShopCart Items")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a ShopCart Item by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    # @classmethod
    # def find_by_name(cls, name):
    #     """Returns all ShopCart Items with the given name

    #     Args:
    #         name (string): the name of the ShopCart Item you want to match
    #     """
    #     logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)
