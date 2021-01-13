from django.db import models

from accounts.models import CustomUser
from business.models import ProductModel, TableModel, BusinessModel

ORDER_STATUS_CHOICES = (
    ('U', 'Unplaced'),
    ('PL', 'Placed'),
    ('S', 'Serving'),
    ('P', 'Paid'),
    ('C', 'Cancelled'),
    ('R', 'Rejected'),
)


class OrderModel(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    table = models.ForeignKey(TableModel, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default='Unplaced', max_length=2)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    deleted = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    handler = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='handler')

    def return_total(self):
        return float(self.total)

    def return_date(self):
        return self.date_ordered.date()

    def __str__(self):
        return f'OrderId: {self.id} / Table: {self.table} / Customer: {self.customer}'

    def set_new_to_false(self):
        self.new = False
        OrderModel.objects.filter(id=self.pk).update(new=False)


class OrderItem(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.product}'
