from django.contrib import admin

from .models import BusinessModel, ProductModel, ProductCategory, TableModel, BusinessCategory,Invitation


class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'manager', 'maps_address', 'displayed_address', 'is_open_now',
    )


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_nr', 'business')
    search_fields = ('table_nr', 'business__business_name')


admin.site.register(BusinessModel, BusinessAdmin)
admin.site.register(ProductModel)
admin.site.register(TableModel, TableAdmin)
admin.site.register(BusinessCategory)
admin.site.register(ProductCategory)
admin.site.register(Invitation)
