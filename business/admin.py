from django.contrib import admin
from .models import BusinessModel, ProductModel, TableModel


class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'manager', 'address', 'is_open_now',
    )


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_nr', 'business')
    search_fields = ('table_nr', 'business__business_name')


admin.site.register(BusinessModel, BusinessAdmin)
admin.site.register(ProductModel)
admin.site.register(TableModel, TableAdmin)
