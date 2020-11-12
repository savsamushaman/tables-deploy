from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView

from tray.models import OrderModel, OrderItem
from .forms import CreateBusinessForm, CreateProductForm
from .models import BusinessModel, ProductModel, TableModel


# Business -----------------------------------------------------
# List
class BusinessListView(LoginRequiredMixin, ListView):
    context_object_name = 'owned'
    template_name = 'business/business/business_list.html'
    model = BusinessModel

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BusinessListView, self).get_context_data(**kwargs)
        context['owned'] = BusinessModel.objects.filter(manager=self.request.user)
        return context


# Create
class CreateBusinessView(LoginRequiredMixin, CreateView):
    model = BusinessModel
    template_name = 'business/business/create_business.html'
    form_class = CreateBusinessForm
    success_url = reverse_lazy('owned:owned_list')

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)


# Edit
class BusinessEditView(LoginRequiredMixin, UpdateView):
    model = BusinessModel
    template_name = 'business/business/edit_business.html'
    context_object_name = 'business'
    fields = ['business_name', 'short_description', 'email', 'phone_nr', 'address', 'all_tables', 'available_tables',
              'is_open_now']
    success_url = reverse_lazy('owned:owned_list')

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).post(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(BusinessEditView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def form_valid(self, form):
        form.instance.save()
        return HttpResponseRedirect('/owned/')


# Product -----------------------------------------------------
# List
class ProductListView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'business/business/products.html'
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


# Create
class CreateProductView(LoginRequiredMixin, CreateView):
    model = ProductModel
    template_name = 'business/business/create_product.html'
    success_url = reverse_lazy('user_details')
    form_class = CreateProductForm

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
        form.instance.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateProductView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        return kwargs


# Edit
class ProductEditView(LoginRequiredMixin, UpdateView):
    model = ProductModel
    template_name = 'business/business/edit_product.html'
    context_object_name = 'product'
    success_url = reverse_lazy('user_details')
    form_class = CreateProductForm

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

    def form_valid(self, form):
        form.instance.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_form_kwargs(self):
        kwargs = super(ProductEditView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        return kwargs


# Delete
class ProductDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            ProductModel.objects.get(business__slug=slug, pk=self.kwargs['pk']).delete()
            return redirect('owned:products_list', slug=slug)
        else:
            raise Http404


# Table -----------------------------------------------------
# List
class TableListView(LoginRequiredMixin, ListView):
    model = TableModel
    template_name = 'business/business/tables_list.html'
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


# Create
class CreateTableView(LoginRequiredMixin, CreateView):
    model = TableModel
    template_name = 'business/business/create_table.html'
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
        form.instance.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super(CreateTableView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context


# Update
class TableEditView(LoginRequiredMixin, UpdateView):
    model = TableModel
    template_name = 'business/business/edit_table.html'
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

    def form_valid(self, form):
        form.instance.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super(TableEditView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context


# Delete
class TableDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            TableModel.objects.get(business__slug=slug, pk=self.kwargs['pk']).delete()
            return redirect('owned:tables_list', slug=slug)
        else:
            raise Http404


# Feed -----------------------------------------------------
class FeedView(LoginRequiredMixin, View):
    template_name = 'business/feed/feed.html'

    def get(self, request, *args, **kwargs):
        order_models = OrderModel.objects.filter(business__slug=self.kwargs['slug'], status__regex='PL|S')

        order_information = []
        for order in order_models:
            entry = {'customer': order.customer,
                     'id': order.order_id,
                     'table': order.table,
                     'pk': order.pk,
                     'status': order.status,
                     'items': OrderItem.objects.filter(order=order), }

            order_information.append(entry)

        context = {'orders': order_information}
        context['slug'] = self.kwargs['slug']

        return render(request, self.template_name, context)


# Process Order
class ProcessOrder(View):
    def get(self, request, *args, **kwargs):
        print(self.kwargs)
        order_pk = self.kwargs['pk']
        order = OrderModel.objects.get(pk=order_pk)
        order.status = 'S'
        order.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
