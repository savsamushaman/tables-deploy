from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .forms import RegisterUserForm
from .models import CustomUser


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/register.html'


class MyLoginView(LoginView):
    template_name = "accounts/login.html"


class MyLogoutView(LogoutView):
    template_name = "accounts/logout.html"


class UserDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'accounts/user_details.html'
        user_details = CustomUser.objects.get(pk=request.user.pk)
        context = {'user': user_details}
        return render(request, template_name, context)
