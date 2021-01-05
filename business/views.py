from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, FormView

from accounts.models import CustomUser
from tray.models import OrderModel, OrderItem
from .forms import CreateBusinessForm, ProductForm, UpdateBusinessForm, TableForm, UpdateTableForm, MenuPointForm, \
    InviteForm
from .models import BusinessModel, ProductModel, TableModel, ProductCategory, Invitation, GalleryImageModel


def check_if_allowed(request, slug, allow_staff=False):
    business = BusinessModel.objects.get(slug=slug)
    user = request.user
    if business.is_active:
        if business.manager == user or user in business.admins.all():
            return True
        if allow_staff:
            if user in business.staff.all():
                return True
        return False
    return False


# Business -----------------------------------------------------
# List
class BusinessListView(LoginRequiredMixin, ListView):
    context_object_name = 'your_places'
    queryset = None
    template_name = 'business/business/business_list.html'
    model = BusinessModel

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BusinessListView, self).get_context_data(**kwargs)
        user = self.request.user
        is_admin = user.admins.all()
        is_staff = user.staff.all()
        places = (is_admin | is_staff).distinct()
        context['your_places'] = places
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

    def get_success_url(self):
        self.object.admins.add(self.object.manager)
        self.object.save()
        return super(CreateBusinessView, self).get_success_url()


# Edit
class BusinessEditView(LoginRequiredMixin, UpdateView):
    model = BusinessModel
    template_name = 'business/business/update_business.html'
    context_object_name = 'business'
    success_url = reverse_lazy('owned:owned_list')
    form_class = UpdateBusinessForm

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(BusinessEditView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:owned_list")

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            return super(BusinessEditView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

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


class BusinessDeleteView(LoginRequiredMixin, DeleteView):
    model = BusinessModel
    template_name = 'business/business/delete_business.html'
    context_object_name = 'business'

    def get_success_url(self):
        return reverse_lazy('owned:owned_list')

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            return super(BusinessDeleteView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            business = BusinessModel.objects.get(slug=slug)
            orders = OrderModel.objects.filter(business=business, status__regex='PL|S')
            tables = TableModel.objects.filter(business=business)
            for order in orders:
                order.status = 'C'
                order.save()
            for table in tables:
                business.current_guest -= len(table.current_guests.all())
                table.current_guests.clear()
                table.delete()

            business.is_active = False
            business.save()
            messages.add_message(request, messages.INFO, f'{business.business_name} was deleted successfully')
            return redirect('owned:owned_list')
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)


# Product -----------------------------------------------------
# List
class ProductListView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'business/business/product_list.html'
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(ProductListView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

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
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateProductView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateProductView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        form.instance.save()
        messages.add_message(self.request, level=messages.INFO,
                             message=f'Product {form.instance.name} was created successfully')
        return super(CreateProductView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Product Creation Failed')
        return super(CreateProductView, self).form_invalid(form)

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
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(ProductEditView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(ProductEditView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

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
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            product = ProductModel.objects.get(business__slug=slug, pk=self.kwargs['pk'])
            product.deleted = True
            product.save()
            messages.add_message(request, level=messages.INFO,
                                 message=f'Product {product.name} was deleted successfully')
            return redirect('owned:products_list', slug=slug)
        else:
            messages.add_message(request, messages.ERROR, 'Action Not allowed')
            return redirect("owned:business_update", slug=slug)


# Table -----------------------------------------------------
# List
class TableListView(LoginRequiredMixin, ListView):
    model = TableModel
    template_name = 'business/business/table_list.html'
    context_object_name = 'tables'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(TableListView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def get_context_data(self, **kwargs):
        context = super(TableListView, self).get_context_data(**kwargs)
        context['tables'] = TableModel.objects.filter(business__slug=self.kwargs['slug']).order_by(
            'table_nr')
        context['slug'] = self.kwargs['slug']
        return context


# Create
class CreateTableView(LoginRequiredMixin, CreateView):
    model = TableModel
    template_name = 'business/business/create_table.html'
    form_class = TableForm

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateTableView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateTableView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def get_context_data(self, **kwargs):
        context = super(CreateTableView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        try:
            form.instance.save()
        except IntegrityError:
            form.add_error('table_nr', 'Table already exists')
            messages.add_message(self.request, messages.ERROR,
                                 f'Table with number {form.instance.table_nr} already exists ')
            return super(CreateTableView, self).get(self.request, self.args, self.kwargs)
        business.all_tables += 1
        business.available_tables += 1
        business.save()
        messages.add_message(self.request, messages.INFO, f'Table {form.instance.table_nr} was created successfully')
        return super(CreateTableView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('owned:create_table', kwargs={'slug': self.kwargs['slug']})


# Update
class TableEditView(LoginRequiredMixin, UpdateView):
    model = TableModel
    template_name = 'business/business/update_table.html'
    context_object_name = 'table'
    form_class = UpdateTableForm

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(TableEditView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(TableEditView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def form_valid(self, form):
        try:
            form.instance.save()
        except IntegrityError:
            form.add_error('table_nr', 'Table already exists')
            messages.add_message(self.request, messages.ERROR,
                                 f'Table with number {form.instance.table_nr} already exists ')
            return super(TableEditView, self).get(self.request, self.args, self.kwargs)

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
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            try:
                business = BusinessModel.objects.get(sluge=slug)
                table = TableModel.objects.get(business__slug=slug, pk=self.kwargs['pk'])
            except (BusinessModel.DoesNotExist, TableModel.DoesNotExist):
                messages.add_message(request, level=messages.INFO,
                                     message=f'Bad request')
                messages.add_message(request, messages.ERROR, 'Object does not exist')
                return redirect("owned:business_update", slug=slug)

            if len(table.current_guests.all()) == 0:
                business.available_tables -= 1
            business.current_guests -= len(table.current_guests.all())
            table.current_guests.clear()
            business.all_tables -= 1

            business.save()
            table.delete()
            messages.add_message(request, level=messages.INFO,
                                 message=f'Table {table.table_nr} was deleted successfully')
            return redirect('owned:tables_list', slug=slug)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)


# Menu point -----------------------------------------------------
# Create

class CreateMenuPoint(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = MenuPointForm
    template_name = 'business/business/create_menupoint.html'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateMenuPoint, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(CreateMenuPoint, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        business = BusinessModel.objects.get(slug=slug)
        form.instance.business = business
        try:
            form.instance.save()
        except IntegrityError:
            form.add_error('category_name', 'Table already exists')
            messages.add_message(self.request, messages.ERROR,
                                 f'Menupoint {form.instance.category_name} already exists ')
            return super(CreateMenuPoint, self).get(self.request, self.args, self.kwargs)
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
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(MenuPointListView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

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
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(MenuPointEditView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(MenuPointEditView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def form_valid(self, form):
        try:
            form.instance.save()
        except IntegrityError:
            form.add_error('category_name', 'Table already exists')
            messages.add_message(self.request, messages.ERROR,
                                 f'Menupoint {form.instance.category_name} already exists ')
            return super(MenuPointEditView, self).get(self.request, self.args, self.kwargs)
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
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            menupoint = ProductCategory.objects.get(business__slug=slug, pk=self.kwargs['pk'])
            products = ProductModel.objects.filter(category=menupoint)

            for product in products:
                product.category = None
                product.save()

            menupoint.deleted = True
            messages.add_message(request, level=messages.INFO,
                                 message=f'Menupoint {menupoint.category_name} was deleted successfully')

            menupoint.category_name = f'deleted-menupoint-{menupoint.pk}-{menupoint.business.business_name}'
            menupoint.save()

            return redirect('owned:menupoints_list', slug=slug)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)


class StaffListView(LoginRequiredMixin, FormView):
    model = CustomUser
    template_name = 'business/business/staff_list.html'
    form_class = InviteForm

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            return super(StaffListView, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            return super(StaffListView, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def get_context_data(self, **kwargs):
        context = super(StaffListView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['staff'] = BusinessModel.objects.get(slug=slug).staff.all()
        context['admins'] = BusinessModel.objects.get(slug=slug).admins.all()
        context['pending_invitations'] = Invitation.objects.filter(business__slug=slug, status='S')
        context['slug'] = slug

        return context

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(self.request, slug)
        if allowed:
            business = BusinessModel.objects.get(slug=self.kwargs['slug'])
            username = form.cleaned_data['username']
            current_user = self.request.user
            try:
                invited_user = CustomUser.objects.get(username=username)
                if invited_user in business.staff.all() or invited_user in business.admins.all():
                    messages.add_message(self.request, messages.INFO,
                                         f'User {username} is already a staff member/ admin')
                    return super(StaffListView, self).get(self.request, self.args, self.kwargs)

                is_invited = len(Invitation.objects.filter(to_user=invited_user, business=business, status='S'))

                if not is_invited:
                    Invitation.objects.create(from_user=current_user, to_user=invited_user, business=business,
                                              status='S')
                    messages.add_message(self.request, messages.INFO,
                                         f'You invited {username} to {business.business_name} staff')
                else:
                    messages.add_message(self.request, messages.INFO, f'User {username} is already invited')
                return super(StaffListView, self).form_valid(form)
            except CustomUser.DoesNotExist:
                messages.add_message(self.request, messages.ERROR, f'User {username} not found')
                return super(StaffListView, self).get(self.request, self.args, self.kwargs)
        else:
            return HttpResponseForbidden()

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:staff_list', kwargs={'slug': slug})


class StaffListUpdate(View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            business = BusinessModel.objects.get(slug=self.kwargs['slug'])
            user = CustomUser.objects.get(id=self.kwargs['user_pk'])
            # from_admin evaluates to True if a 0 integer is passed in the url, same with add
            admin_group = self.kwargs['group']
            remove = self.kwargs['action']
            admins = business.admins.all()
            staff = business.staff.all()

            if remove:
                if admin_group:
                    if user in admins:
                        if len(admins) - 1 <= 0:
                            messages.add_message(request, messages.ERROR,
                                                 'Action not possible, at least 1 admin is required')
                        else:
                            business.admins.remove(user)
                            messages.add_message(request, messages.INFO, f'{user.username} was removed from admins')
                    else:
                        messages.add_message(request, messages.ERROR, f'{user.username} is not an admin')
                else:
                    if user in staff:
                        business.staff.remove(user)
                        messages.add_message(request, messages.INFO, f'{user.username} was removed from staff')
                    else:
                        messages.add_message(request, messages.ERROR, f'{user.username} is not a staff member')
                return redirect('owned:staff_list', slug=business.slug)
            else:
                if admin_group:
                    if user not in admins:
                        business.admins.add(user)
                        messages.add_message(request, messages.INFO, f'{user.username} was added to admins')
                    else:
                        messages.add_message(request, messages.ERROR,
                                             f'{user.username} is already an admin')
                else:
                    if user not in staff:
                        business.staff.add(user)
                        messages.add_message(request, messages.INFO, f'{user.username} was added to staff')
                    else:
                        messages.add_message(request, messages.INFO, f'{user.username} is already a staff member')

                return redirect('owned:staff_list', slug=business.slug)

        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)


class CancelInvitation(View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug)
        if allowed:
            business = BusinessModel.objects.get(slug=slug)
            invitation = Invitation.objects.get(pk=self.kwargs['pk'], business=business)
            if invitation.status != 'C':
                invitation.status = 'C'
                invitation.save()
                messages.add_message(request, messages.INFO, 'Invitation was cancelled')
                return redirect('owned:staff_list', slug=business.slug)
            else:
                messages.add_message(request, messages.ERROR, 'Invitation was already accepted or declined')
                return redirect('owned:staff_list', slug=business.slug)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)


# Feed -----------------------------------------------------
class FeedView(LoginRequiredMixin, View):
    template_name = 'business/business/feed_page.html'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        business = BusinessModel.objects.get(slug=slug)
        order_models = OrderModel.objects.filter(business__slug=slug, status__regex='PL|S')

        order_information = []
        for order in order_models:
            entry = {'customer': order.customer,
                     'table': order.table,
                     'pk': order.pk,
                     'status': order.status,
                     'items': OrderItem.objects.filter(order=order),
                     'total': order.total,
                     'handler': order.handler,
                     }

            order_information.append(entry)

        context = {'orders': order_information, 'slug': slug, 'business_name': business.business_name}

        return render(request, self.template_name, context)


# Gallery -----------------------------------------------------

class Gallery(LoginRequiredMixin, CreateView):
    model = GalleryImageModel
    template_name = 'business/business/gallery.html'
    fields = ('source',)

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(Gallery, self).get(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Access Denied')
            return redirect("owned:business_update", slug=slug)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            return super(Gallery, self).post(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Action not allowed')
            return redirect("owned:business_update", slug=slug)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Gallery, self).get_context_data(**kwargs)
        business = BusinessModel.objects.get(slug=self.kwargs['slug'])
        images = GalleryImageModel.objects.filter(belongs=business)
        context['gallery'] = images
        context['slug'] = self.kwargs['slug']
        return context

    def form_valid(self, form):
        slug = self.kwargs['slug']
        form.instance.belongs = BusinessModel.objects.get(slug=slug)
        return super(Gallery, self).form_valid(form)

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('owned:gallery', kwargs={'slug': slug})


class DeleteGalleryItem(View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        allowed = check_if_allowed(request, slug, allow_staff=True)
        if allowed:
            gallery_item = GalleryImageModel.objects.get(belongs__slug=slug, pk=self.kwargs['pk'])
            gallery_item.delete()
            messages.add_message(request, level=messages.INFO,
                                 message=f'Image removed from gallery')
            return redirect('owned:gallery', slug=slug)
        else:
            messages.add_message(request, messages.ERROR, 'Action Not allowed')
            return redirect("owned:business_update", slug=slug)
