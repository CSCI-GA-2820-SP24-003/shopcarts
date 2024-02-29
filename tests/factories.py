"""Test Factory"""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import ShopCart, ShopCartStatus, ShopCartItem


class ShopCartFactory(factory.Factory):
    """Creates fake shop cart instances"""

    class Meta:
        """Maps factory to data model"""

        model = ShopCart

    id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"sc-{n}")
    total_price = FuzzyDecimal(0.00, 200.00)
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


class ShopCartItemFactory(factory.Factory):
    """Creates fake shop cart item instances"""

    class Meta:
        """Maps factory tp data model"""

        model = ShopCartItem

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    shop_cart_id = None
    quantity = factory.Sequence(lambda n: n)
    price = FuzzyDecimal(0.00, 10.00)
    shop_cart = factory.SubFactory(ShopCartFactory)
