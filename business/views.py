import json

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest, \
    HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView

from tray.models import OrderModel, OrderItem
from .forms import CreateBusinessForm, ProductForm, UpdateBusinessForm, TableForm, UpdateTableForm, MenuPointForm
from .models import BusinessModel, ProductModel, TableModel, ProductCategory


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
        messages.add_message(self.request, messages.INFO, f'{form.instance.business_name} was created successfully')
        return super().form_valid(form)


# Edit
class BusinessEditView(LoginRequiredMixin, UpdateView):
    model = BusinessModel
    template_name = 'business/business/update_business.html'
    context_object_name = 'business'
    success_url = reverse_lazy('owned:owned_list')
    form_class = UpdateBusinessForm

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(BusinessEditView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(BusinessEditView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def form_valid(self, form):
        form.instance.save()
        messages.add_message(self.request, messages.INFO, f'{form.instance.business_name} was updated successfully')
        return super(BusinessEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, f'{form.instance.business_name} update failed')
        return super(BusinessEditView, self).form_invalid(form)


# Product -----------------------------------------------------
# List
class ProductListView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'business/business/product_list.html'
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductListView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['products'] = ProductModel.objects.filter(business__slug=slug, deleted=False).order_by('category')
        context['slug'] = slug
        return context


# Create
class CreateProductView(LoginRequiredMixin, CreateView):
    model = ProductModel
    template_name = 'business/business/create_product.html'
    form_class = ProductForm

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateProductView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateProductView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        form.instance.save()
        messages.add_message(self.request, level=messages.INFO,
                             message=f'Product {form.instance.name} was created successfully')
        return super(CreateProductView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateProductView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        return kwargs

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:create_product', kwargs={'slug': slug})


# Edit
class ProductEditView(LoginRequiredMixin, UpdateView):
    model = ProductModel
    template_name = 'business/business/update_product.html'
    context_object_name = 'product'
    form_class = ProductForm

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductEditView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(ProductEditView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        form.instance.save()
        messages.add_message(self.request, level=messages.INFO,
                             message=f'Product {form.instance.name} was updated successfully')
        return super(ProductEditView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ProductEditView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        return kwargs

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:products_list', kwargs={'slug': slug})


# Delete
class ProductDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            product = ProductModel.objects.get(business__slug=slug, pk=self.kwargs['pk'])
            product.deleted = True
            product.save()
            messages.add_message(request, level=messages.INFO,
                                 message=f'Product {product.name} was deleted successfully')
            return redirect('owned:products_list', slug=slug)
        else:
            return HttpResponseForbidden()


# Table -----------------------------------------------------
# List
class TableListView(LoginRequiredMixin, ListView):
    model = TableModel
    template_name = 'business/business/table_list.html'
    context_object_name = 'tables'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableListView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(TableListView, self).get_context_data(**kwargs)
        context['tables'] = TableModel.objects.filter(business__slug=self.kwargs['slug'], deleted=False).order_by(
            'table_nr')
        context['slug'] = self.kwargs['slug']
        return context


# Create
class CreateTableView(LoginRequiredMixin, CreateView):
    model = TableModel
    template_name = 'business/business/create_table.html'
    form_class = TableForm

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateTableView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateTableView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(CreateTableView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        form.instance.save()
        business.all_tables += 1
        business.save()
        messages.add_message(self.request, messages.INFO, f'Table {form.instance.table_nr} was created successfully')
        return super(CreateTableView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('owned:tables_list', kwargs={'slug': self.kwargs['slug']})


# Update
class TableEditView(LoginRequiredMixin, UpdateView):
    model = TableModel
    template_name = 'business/business/update_table.html'
    context_object_name = 'table'
    form_class = UpdateTableForm

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableEditView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(TableEditView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        form.instance.save()
        messages.add_message(self.request, messages.INFO, f'Table {form.instance.table_nr} was updated successfully')
        return super(TableEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TableEditView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        context['table'] = TableModel.objects.get(pk=self.kwargs['pk'], business__slug=self.kwargs['slug'])
        return context

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:tables_list', kwargs={'slug': slug})


# Delete
class TableDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            table = TableModel.objects.get(business__slug=slug, pk=self.kwargs['pk'])
            table.deleted = True
            table.save()
            business.all_tables -= 1
            business.save()
            messages.add_message(request, level=messages.INFO,
                                 message=f'Table {table.table_nr} was deleted successfully')
            return redirect('owned:tables_list', slug=slug)
        else:
            return HttpResponseForbidden()


# Menu point -----------------------------------------------------
# Create

class CreateMenuPoint(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = MenuPointForm
    template_name = 'business/business/create_menupoint.html'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateMenuPoint, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(CreateMenuPoint, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        form.instance.save()
        messages.add_message(self.request, level=messages.INFO,
                             message=f'Menu Point {form.instance.category_name} was created successfully')
        return super(CreateMenuPoint, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateMenuPoint, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:create_menu_point', kwargs={'slug': slug})


# List

class MenuPointListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'business/business/menupoint_list.html'
    context_object_name = 'menupoints'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(MenuPointListView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(MenuPointListView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['menupoints'] = ProductCategory.objects.filter(business__slug=slug, deleted=False).order_by(
            'category_name')
        context['slug'] = slug
        return context


# Edit

class MenuPointEditView(LoginRequiredMixin, UpdateView):
    model = ProductCategory
    template_name = 'business/business/update_menupoint.html'
    context_object_name = 'menupoint'
    form_class = MenuPointForm

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(MenuPointEditView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            return super(MenuPointEditView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        form.instance.save()
        messages.add_message(self.request, level=messages.INFO,
                             message=f'Menu Point {form.instance.category_name} was updated successfully')
        return super(MenuPointEditView, self).form_valid(form)

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:menupoints_list', kwargs={'slug': slug})


# Delete

class MenuPointDelete(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        if request.user == business.manager:
            menupoint = ProductCategory.objects.get(business__slug=slug, pk=self.kwargs['pk'])

            try:
                products = ProductModel.objects.filter(category=menupoint)
            except:
                products = None

            if products:
                for product in products:
                    product.category = None

            menupoint.deleted = True
            menupoint.save()

            messages.add_message(request, level=messages.INFO,
                                 message=f'Menupoint {menupoint.category_name} was deleted successfully')
            return redirect('owned:menupoints_list', slug=slug)
        else:
            return HttpResponseForbidden()


# Feed -----------------------------------------------------
class FeedView(LoginRequiredMixin, View):
    template_name = 'business/feed/feed.html'

    def get(self, request, *args, **kwargs):
        order_models = OrderModel.objects.filter(business__slug=self.kwargs['slug'], status__regex='PL|S')

        order_information = []
        for order in order_models:
            entry = {'customer': order.customer,
                     'table': order.table,
                     'pk': order.pk,
                     'status': order.status,
                     'items': OrderItem.objects.filter(order=order), }

            order_information.append(entry)

        context = {'orders': order_information, 'slug': self.kwargs['slug']}

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


# needs redesigning - add many to many to order instead of order item
class ReturnOrders(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('POST')

    def post(self, request, *args, **kwargs):
        data = json.loads(self.request.body)
        business_slug = data.get('business', None)
        if business_slug:
            if self.request.user == BusinessModel.objects.get(slug=business_slug).manager:
                response = OrderModel.objects.filter(business__slug=business_slug, status__regex='PL|S')
                response = [result.__repr__() for result in response]

                items = dict()
                for order in response:
                    items[f'{order["orderid"]}'] = OrderItem.objects.filter(order_id=order['orderid'])
                    items[f'{order["orderid"]}'] = [result.__repr__() for result in items[f'{order["orderid"]}']]
                    order['items'] = items[f'{order["orderid"]}']

                return JsonResponse({'results': response})
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseBadRequest()

# signals

# @receiver(post_save, sender=TableModel)
# def update_available_table(sender, instance, created, **kwargs):
#     if not instance.current_guests:
#         instance.business.available_tables +=1
#     else:
#         instance
