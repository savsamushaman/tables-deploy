from django.contrib import admin
from .models import OrderModel, OrderItem

admin.site.register(OrderModel)
admin.site.register(OrderItem)

