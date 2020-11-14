from django.db import models

from accounts.models import CustomUser
from business.models import ProductModel, TableModel, BusinessModel

ORDER_STATUS_CHOICES = (
    ('U', 'Unplaced'),
    ('PL', 'Placed'),
    ('S', 'Serving'),
    ('P', 'Paid')
)


class OrderModel(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, )
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE, null=True)
    table = models.ForeignKey(TableModel, on_delete=models.CASCADE, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default='Unplaced', max_length=2)
    order_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.id} - {self.table} - {self.customer}'


class OrderItem(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.product}'
