from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LogoutView, LoginView
from .forms import RegisterUserForm


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/register.html'


class MyLoginView(LoginView):
    template_name = "accounts/login.html"


class MyLogoutView(LogoutView):
    template_name = "accounts/logout.html"
