from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CountryModel
from .forms import RegisterUserFormAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = RegisterUserFormAdmin
    prepopulated_fields = {'username': ('first_name', 'last_name'), }
    ordering = ('id', 'email')

    add_fieldsets = (
        ("User Data", {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'username', 'password1', 'password2', 'email', 'phone_number',
            ),
        }),
        ('User Privileges', {'classes': ('wide'),
                             'fields': ('is_superuser', 'is_staff', 'is_active')})
    )

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            "Additional data",
            {
                'fields': (
                    'phone_number',
                    'slug',
                    'country',
                    'device'

                )
            }

        )
    )
    list_display = ('id', 'username', 'device', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username__contains', 'device__contains', 'email__contains',)


class CountryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency')
    search_fields = ('name__contains', 'currency')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CountryModel, CountryModelAdmin)
