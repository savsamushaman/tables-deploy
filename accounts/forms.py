from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

from accounts.models import CustomUser


class SelfClearField(forms.TextInput):
    def get_context(self, name, value, attrs):
        value = None
        return super(SelfClearField, self).get_context(name, value, attrs)


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=SelfClearField(attrs={'class': 'input100'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100'}))


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
        exclude = ['is_superuser', 'is_active', 'is_staff', 'groups', 'user_permissions', 'slug', 'date_joined',
                   'last_login', 'password', 'device']

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'input--style-5', }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'input--style-5', }), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                              'class': 'input--style-5', }), required=False)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your e-mail address', 'class': 'input--style-5'}))

    phone = forms.CharField(widget=forms.TextInput({'placeholder': 'Optional', 'class': 'input--style-5'}),
                            required=False)

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'input--style-5',
                                                                  }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password Again',
                                                                  'class': 'input--style-5',
                                                                  }))


class RegisterUserFormAdmin(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'country']

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'First Name', }),
        required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'Last Name', }),
        required=False)
    phone_number = forms.CharField(widget=forms.TextInput({'class': 'input--style-5', 'placeholder': 'Phone Number', }),
                                   required=False)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'input--style-5', 'placeholder': 'Email address', }))


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ["old_password", 'new_password1', 'new_password2']

    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100', }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100', }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100', }))
