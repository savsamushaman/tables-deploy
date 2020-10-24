from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser
from .forms import RegisterUserForm, CreateProductForm
from business.models import BusinessModel, ProductModel
from django.http import Http404


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
        business = BusinessModel.objects.filter(manager=request.user)
        context = {'user': user_details, 'businesses': business}
        return render(request, template_name, context)

# add def get def post
class BusinessEditView(LoginRequiredMixin, UpdateView):
    model = BusinessModel
    template_name = 'accounts/business/edit_business.html'
    context_object_name = 'business'
    fields = ['business_name', 'short_description', 'email', 'phone_nr', 'address', 'all_tables', 'available_tables',
              'is_open_now']
    success_url = reverse_lazy('user_details')

    def get_context_data(self, **kwargs):
        context = super(BusinessEditView, self).get_context_data(**kwargs)
        context['products'] = ProductModel.objects.filter(business__slug=self.kwargs['slug'])
        return context


class ProductEditView(LoginRequiredMixin, UpdateView):
    model = ProductModel
    template_name = 'accounts/business/edit_product.html'
    context_object_name = 'product'
    fields = ['name', 'description', 'price', 'service']
    success_url = reverse_lazy('user_details')

    def get_context_data(self, **kwargs):
        context = super(ProductEditView, self).get_context_data(**kwargs)
        print(self.kwargs)
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductEditView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductEditView, self).post(request, *args, **kwargs)
        else:
            raise Http404


# class CreateProductView(LoginRequiredMixin, View):
#     template_name = 'accounts/business/create_product.html'
#     form = CreateProductForm
#
#     def get(self, request, *args, **kwargs):
#         slug = kwargs.get('slug')
#         business = BusinessModel.objects.get(slug=slug)
#         if request.user == business.manager:
#             return render(request, self.template_name, {'form': self.form()})
#         else:
#             raise Http404
#
#     def post(self, request, *args, **kwargs):
#         form = self.form(self.request.POST)
#         if form.is_valid():
#             new_product_data = request.POST.dict()
#             del new_product_data['csrfmiddlewaretoken']
#             slug = kwargs.get('slug')
#             business = BusinessModel.objects.get(slug=slug)
#             ProductModel.objects.create(business=business, **new_product_data)
#             return redirect('user_details')
#         else:
#             return render(request, self.template_name, {'form': self.form()})

class CreateProductView(LoginRequiredMixin, CreateView):
    model = ProductModel
    template_name = 'accounts/business/create_product.html'
    fields = ['name', 'description', 'price', 'service']
    success_url = reverse_lazy('user_details')

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateProductView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateProductView, self).post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        return super().form_valid(form)
