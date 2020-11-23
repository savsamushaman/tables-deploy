from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from tray.models import OrderModel, OrderItem
from .forms import RegisterUserForm, LoginForm
from .models import CustomUser


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:user_details')
        else:
            return super(RegisterUserView, self).get(request, *args, **kwargs)


class MyLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:user_details')
        else:
            return super(MyLoginView, self).get(request, *args, **kwargs)


class MyLogoutView(LogoutView):
    template_name = "accounts/logout.html"


class UserDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'accounts/user_details.html'
        user_details = CustomUser.objects.get(pk=request.user.pk)
        paid_orders = OrderModel.objects.filter(customer=self.request.user, status__in='PC')
        order_history = []
        for order in paid_orders:
            order_items = OrderItem.objects.filter(order=order)
            order_history.append({
                'customer': f'{order.customer}',
                'order_id': f'{order.id}',
                'business': f'{order.business}',
                'table:': f'{order.table}',
                'date_ordered': f'{order.return_date()}',
                'status': f'{order.status}',
                'total': f'{order.total}',
                'items': order_items

            })

        context = {'user': user_details, 'order_history': order_history}
        return render(request, template_name, context)


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_mail.html'


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
