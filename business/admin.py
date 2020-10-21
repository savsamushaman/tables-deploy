from django.contrib import admin
from .models import BusinessModel, ProductModel


class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'manager', 'address', 'is_open_now',
    )


admin.site.register(BusinessModel, BusinessAdmin)
admin.site.register(ProductModel)
