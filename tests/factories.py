"""Test Factory"""

from decimal import Decimal
import random
import factory
from factory.fuzzy import FuzzyDecimal, FuzzyChoice
from service.models import ShopCart, ShopCartItem
from service.models.shop_cart import ShopCartStatus


class DecimalMine(factory.fuzzy.BaseFuzzyAttribute):
    """Generates a random decimal number between low and high with precision."""
    def __init__(self, low, high, precision='0.01'):
        super().__init__()
        self.low = Decimal(low)
        self.high = Decimal(high)
        self.precision = Decimal(precision)

    def fuzz(self):
        value = Decimal(random.uniform(float(self.low), float(self.high))).quantize(self.precision)
        return value


# pylint: disable=too-few-public-methods
class ShopCartFactory(factory.Factory):
    """Creates fake shop cart instances"""
    class Meta:
        """Maps factory to data model"""
        model = ShopCart
    id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"sc-{n}")
    total_price = FuzzyDecimal(0.00, 200.00)
    total_price = DecimalMine(0.00, 200.00)
    status = FuzzyChoice(
        choices=[ShopCartStatus.ACTIVE, ShopCartStatus.PENDING, ShopCartStatus.INACTIVE]
    )

    @factory.post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the Shop Cart Items list"""
        if not create:
            return
        if extracted:
            self.items = extracted


# pylint: disable=too-few-public-methods
class ShopCartItemFactory(factory.Factory):
    """Creates fake shop cart item instances"""
    class Meta:
        """Maps factory tp data model"""
        model = ShopCartItem

    id = factory.Sequence(lambda n: n)
    shop_cart_id = None
    name = factory.Sequence(lambda n: f"i-{n}")
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Sequence(lambda n: n)
    price = FuzzyDecimal(0.00, 10.00)
    shop_cart = factory.SubFactory(ShopCartFactory)
