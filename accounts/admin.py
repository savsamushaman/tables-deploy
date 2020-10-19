from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import RegisterUserFormAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = RegisterUserFormAdmin
    prepopulated_fields = {'username': ('first_name', 'last_name'), }

    add_fieldsets = (
        ("User Data", {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'username', 'password1', 'password2', 'email', 'phone_number', 'address',
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
                    'address',
                    'slug',

                )
            }

        )
    )


admin.site.register(CustomUser, CustomUserAdmin)
