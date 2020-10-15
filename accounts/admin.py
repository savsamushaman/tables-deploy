from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import RegisterUserForm


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = RegisterUserForm
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

                )
            }

        )
    )


admin.site.register(CustomUser, CustomUserAdmin)
