"""
Models for ShopCarts Service

All of the models are stored in this module
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class ShopCartStatus(Enum):
    """Enumeration of different shop cart statuses"""

    # An item has been added to the shop cart
    ACTIVE = 0
    # User reached last step of checkout
    PENDING = 1
    # Order was fulfilled or cart was abandoned
    INACTIVE = 3


class ShopCart(db.Model):
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
    status = db.Column(
        db.Enum(
            ShopCartStatus, nullable=False, server_default=(ShopCartStatus.ACTIVE.name)
        )
    )

    def __repr__(self):
        return f"<ShopCart {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a ShopCart to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a ShopCart to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a ShopCart from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a ShopCart into a dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "total_price": self.total_price,
            "status": self.status,
        }

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
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
        """Returns all of the ShopCarts in the database"""
        logger.info("Processing all ShopCarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a ShopCart by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCart you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
