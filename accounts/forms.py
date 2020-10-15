from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
