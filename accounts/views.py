from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser
from .forms import RegisterUserForm
from business.models import BusinessModel, ProductModel, TableModel
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


# Edit Business
class BusinessEditView(LoginRequiredMixin, UpdateView):
    model = BusinessModel
    template_name = 'accounts/business/edit_business.html'
    context_object_name = 'business'
    fields = ['business_name', 'short_description', 'email', 'phone_nr', 'address', 'all_tables', 'available_tables',
              'is_open_now']
    success_url = reverse_lazy('user_details')

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).post(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(BusinessEditView, self).get_context_data(**kwargs)
        context['products'] = ProductModel.objects.filter(business__slug=self.kwargs['slug'])
        context['slug'] = self.kwargs['slug']
        return context


# Product list
class ProductListView(ListView):
    model = ProductModel
    template_name = 'accounts/business/products.html'
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductListView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['products'] = ProductModel.objects.filter(business__slug=self.kwargs['slug'])
        context['slug'] = self.kwargs['slug']
        return context


# Create product ####
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


# Edit a product ####
class ProductEditView(LoginRequiredMixin, UpdateView):
    model = ProductModel
    template_name = 'accounts/business/edit_product.html'
    context_object_name = 'product'
    fields = ['name', 'description', 'price', 'service']
    success_url = reverse_lazy('user_details')

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


# table list
class TableListView(ListView):
    model = TableModel
    template_name = 'accounts/business/tables_list.html'
    context_object_name = 'tables'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableListView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(TableListView, self).get_context_data(**kwargs)
        context['tables'] = TableModel.objects.filter(business__slug=self.kwargs['slug'])
        context['slug'] = self.kwargs['slug']
        return context


# create table
class CreateTableView(LoginRequiredMixin, CreateView):
    model = TableModel
    template_name = 'accounts/business/create_table.html'
    fields = ['table_nr']
    success_url = reverse_lazy('user_details')

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateTableView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateTableView, self).post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        return super().form_valid(form)


# update table
class TableEditView(LoginRequiredMixin, UpdateView):
    model = TableModel
    template_name = 'accounts/business/edit_table.html'
    context_object_name = 'table'
    fields = ['table_nr']
    success_url = reverse_lazy('user_details')

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableEditView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableEditView, self).post(request, *args, **kwargs)
        else:
            raise Http404
