from django.test import TestCase
from .models import DiscountMaster

class DiscountMasterTestCase(TestCase):
    def test_fixed_discount(self):
        discount = DiscountMaster(description='Fixed 100', discount_value='100', temporary_price=500)
        self.assertEqual(discount.calculate_discounted_price(), 400)

    def test_percentage_discount(self):
        discount = DiscountMaster(description='10% Off', discount_value='10%', temporary_price=500)
        self.assertAlmostEqual(discount.calculate_discounted_price(), 450)

    def test_invalid_discount(self):
        discount = DiscountMaster(description='Invalid', discount_value='abc', temporary_price=500)
        self.assertEqual(discount.calculate_discounted_price(), 500)