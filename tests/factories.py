"""Test Factory"""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import ShopCart, ShopCartStatus


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
