
from django.db import models
from decimal import Decimal

class DiscountMaster(models.Model):
    discount_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    discount_value = models.CharField(max_length=20, help_text="Enter a number for fixed discount or number followed by % for percentage discount (e.g., 100 or 10%)")
    temporary_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price for discount calculation")

    from decimal import Decimal
    def calculate_discounted_price(self):
        if self.discount_value.endswith('%'):
            percent = float(self.discount_value.rstrip('%'))
            return self.temporary_price * Decimal(1 - percent / 100)
        else:
            try:
                discount = Decimal(self.discount_value)
                return self.temporary_price - discount
            except Exception:
                return self.temporary_price

    def __str__(self):
        return f"{self.description} ({self.discount_value})"