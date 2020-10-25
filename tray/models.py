from django.db import models

from accounts.models import CustomUser
from business.models import ProductModel, TableModel, BusinessModel


class OrderModel(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.DO_NOTHING, null=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    table = models.ForeignKey(TableModel, on_delete=models.DO_NOTHING, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False, null=True, blank=True)
    order_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.id} - {self.table} - {self.customer}'


class OrderItem(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(OrderModel, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f'x{self.quantity} {self.product}'
