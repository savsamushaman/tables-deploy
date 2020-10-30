from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from business.models import ProductModel
from django.forms import ModelForm


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
        exclude = ['is_superuser', 'is_active', 'is_staff', 'groups', 'user_permissions', 'slug', 'date_joined',
                   'last_login', 'password']


class RegisterUserFormAdmin(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CreateProductForm(ModelForm):
    class Meta:
        model = ProductModel
        fields = '__all__'
        exclude = ['business']
