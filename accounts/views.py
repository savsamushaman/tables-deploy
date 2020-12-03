from django.contrib.auth import views as auth_views
from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView, PasswordChangeView
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView

from business.models import TableModel
from tray.models import OrderModel, OrderItem
from .forms import RegisterUserForm, LoginForm, UpdateUserForm, ChangePasswordForm
from .models import CustomUser


def check_user(request):
    if request.user.is_authenticated:
        customer = request.user
        return customer
    else:
        device = request.COOKIES.get('device', None)
        if device:
            try:
                customer = CustomUser.objects.get(device=device)
                return customer
            except:
                return None
        else:
            return HttpResponseBadRequest


def clear_session(request, **kwargs):
    session = request.session.get('current_order', None)

    if session:
        customer = check_user(request)

        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest

        if customer and not kwargs['clear_tray']:
            table_nr = session['table']
            business_slug = session['business']
            table = TableModel.objects.get(table_nr=table_nr, business__slug=business_slug)
            table.current_guests.remove(customer)
            table.business.current_guests -= 1
            if len(table.current_guests.all()) == 0:
                table.locked = False
                table.business.available_tables += 1
                table.business.save()
            table.save()

            request.session['current_order'] = None
            request.session['tray'] = []

            active_orders = OrderModel.objects.filter(customer=customer, status='PL')
            for order in active_orders:
                order.status = 'C'
                order.save()
        else:
            request.session['tray'] = []


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
    redirect_authenticated_user = True

    def form_valid(self, form):
        clear_session(self.request)
        return super(MyLoginView, self).form_valid(form)


class MyLogoutView(LogoutView):
    template_name = "accounts/logout.html"


class UserDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'accounts/user_details.html'
        user_details = CustomUser.objects.get(pk=request.user.pk)
        finished_orders = OrderModel.objects.filter(customer=self.request.user, status__in='PC').order_by(
            '-date_ordered')
        order_history = []
        for order in finished_orders:
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


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'accounts/update_user.html'
    form_class = UpdateUserForm
    success_url = reverse_lazy('accounts:user_details')

    def get(self, request, *args, **kwargs):
        if self.request.user == CustomUser.objects.get(slug=self.kwargs['slug']):
            return super(UpdateUserView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if self.request.user == CustomUser.objects.get(slug=self.kwargs['slug']):
            return super(UpdateUserView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'User was successfully updated')
        form.save()
        return super(UpdateUserView, self).form_valid(form)


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


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('accounts:change_password_done')
    template_name = 'accounts/change_password_form.html'
    form_class = ChangePasswordForm


class ChangePasswordDoneView(TemplateView):
    template_name = 'accounts/change_password_done.html'


# signals

def cleanup_logout(sender, user, request, **kwargs):
    clear_session(request)


user_logged_out.connect(cleanup_logout)
