from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from business.models import ProductModel, ProductCategory
from django.forms import ModelForm
from django import forms


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

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop('slug', None)
        super(CreateProductForm, self).__init__(*args, **kwargs)

        if slug:
            self.fields['category'].queryset = ProductCategory.objects.filter(business__slug=slug)

