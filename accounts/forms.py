from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'address', 'password1', 'password2']
        exclude = ['is_superuser', 'is_active', 'is_staff', 'groups', 'user_permissions', 'slug', 'date_joined',
                   'last_login', 'password']


class RegisterUserFormAdmin(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
