import json

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest, HttpResponse, \
    HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import View, TemplateView, DetailView

from accounts.models import CustomUser
from accounts.views import check_user, clear_session
from business.models import BusinessModel, ProductModel, TableModel
from .models import OrderItem, OrderModel


class GenerateOrder(View):

    def get(self, request, *args, **kwargs):

        customer = check_user(request, order_generation=True)
        slug = self.kwargs['place']
        try:
            table = TableModel.objects.get(table_nr=self.kwargs['table_nr'], business__slug=slug)
        except TableModel.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Non-existent or missing table")
            self.request.session['current_order'] = None
            self.request.session['tray'] = []
            return redirect('tray:my_tray')

        if table.locked:
            messages.add_message(self.request, messages.ERROR, f'Table {table.table_nr} is locked')
            return redirect('pages:place_detail', slug=slug)

        table.current_guests.add(customer)
        table.business.current_guests += 1

        if len(table.current_guests.all()) == 1:
            table.locked = True
            table.business.available_tables -= 1
            table.business.save()

        table.business.save()
        table.save()
        order = {'customer': str(self.request.user), 'business': slug, 'table': table.table_nr}
        self.request.session['current_order'] = order
        self.request.session['tray'] = []

        has_cookie = request.COOKIES.get('device')

        if has_cookie:
            return redirect('pages:place_detail', slug=slug)
        else:
            response = redirect('pages:place_detail', slug=slug)
            response.set_cookie('device', customer.device)
            return response


class CancelOrder(View):
    def get(self, request, *args, **kwargs):

        response = clear_session(request, clear_tray=kwargs['clear'])
        if response == HttpResponseBadRequest:
            return HttpResponseBadRequest
        elif response == ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'Table not available')
            return redirect('tray:my_tray')
        else:
            return redirect('tray:my_tray')


class PlaceOrder(View):
    def get(self, request, *args, **kwargs):
        slug = self.request.session['current_order']['business']
        table = self.request.session['current_order']['table']

        customer = check_user(request)
        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest()

        business = BusinessModel.objects.get(slug=slug)

        if not business.is_active:
            messages.add_message(request, messages.ERROR, 'Place unavailable')
            request.session['current_order'] = None
            request.session['tray'] = []
            return redirect('tray:my_tray')

        try:
            table = TableModel.objects.get(business=business, table_nr=table)
        except TableModel.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Non-existent or missing table")
            self.request.session['current_order'] = None
            self.request.session['tray'] = []
            return redirect('tray:my_tray')

        if customer not in table.current_guests.all():
            self.request.session['current_order'] = None
            self.request.session['tray'] = []
            messages.add_message(request, messages.ERROR, "You are not sitting at the table currently")
            return redirect('tray:my_tray')

        order = OrderModel.objects.create(business=business, customer=customer, table=table, status='PL')

        total = 0

        for item in self.request.session['tray']:
            product = ProductModel.objects.get(id=item['item_id'], business__slug=slug)
            order_item = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])
            total += order_item.total_price()

        order.total = total
        order.save()

        messages.add_message(request, messages.INFO,
                             "Order Placed")

        self.request.session['tray'] = []

        return redirect('tray:my_tray')


class RemoveItemFromOrder(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        order_items = self.request.session.get('tray', None)
        if order_items:
            for item in order_items:
                if item['item_id'] == pk:
                    order_items.remove(item)
                    break
            self.request.session['tray'] = order_items
        return redirect('tray:my_tray')


def update_tray(request):
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)
    try:
        product_id = int(data['id'])
        action = data['action']

        all_items = request.session.get('tray', None)
        new_value = 0

        if all_items:
            for item in all_items:
                if item['item_id'] == product_id:
                    if action == 'add':
                        item['quantity'] += 1
                        new_value = item['quantity']
                        break
                    elif action == 'remove':
                        item['quantity'] -= 1
                        if item['quantity'] <= 0:
                            new_value = item['quantity']
                            all_items.remove(item)
                            break
                        new_value = item['quantity']
                        break

        request.session['tray'] = all_items
        payload = {'new_value': new_value}

        return JsonResponse(payload)
    except KeyError:
        return HttpResponseBadRequest()


def add_remove_from_tray(request):
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)

    try:
        product_id = int(data['id'])
        action = data['action']
        all_items = request.session['tray']
        all_ids = {key['item_id'] for key in all_items}

        if action == 'add' and product_id not in all_ids:
            new_item = {'item_id': product_id, 'quantity': 1}
            all_items.append(new_item)
            request.session['tray'] = all_items
        elif action == 'remove' and product_id in all_ids:
            for item in all_items:
                if item['item_id'] == product_id:
                    all_items.remove(item)
                    break
            request.session['tray'] = all_items
        response = HttpResponse(status=200)
    except KeyError:
        return HttpResponseBadRequest()

    return response


class TrayListView(TemplateView):
    context_object_name = 'items'
    template_name = 'tray/tray_page.html'

    def get(self, request, *args, **kwargs):
        customer = check_user(request)
        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest()

        session = self.request.session.get('current_order', None)

        if session:
            slug = session['business']
            table = session['table']
            business = BusinessModel.objects.get(slug=slug)
            try:
                table = TableModel.objects.get(business=business, table_nr=table)
            except TableModel.DoesNotExist:
                messages.add_message(self.request, messages.ERROR, "Wrong or missing table")
                self.request.session['current_order'] = None
                self.request.session['tray'] = []
                return redirect('tray:my_tray')

            if customer not in table.current_guests.all():
                self.request.session['current_order'] = None
                self.request.session['tray'] = []
                messages.add_message(self.request, messages.ERROR, "You are not sitting at the table currently")
                return redirect('tray:my_tray')

            return super(TrayListView, self).get(request, *args, **kwargs)

        return super(TrayListView, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):

        session = self.request.session.get('current_order', None)

        if session:
            slug = session['business']
            table = session['table']

            business = BusinessModel.objects.get(slug=slug)
            table = TableModel.objects.get(business=business, table_nr=table)

            if self.request.user.is_authenticated:
                customer = self.request.user
            else:
                device = self.request.COOKIES.get('device')
                customer, created = CustomUser.objects.get_or_create(device=device)

            order = OrderModel(business=business, customer=customer, table=table)

            on_the_tray = []
            total = 0

            for item in self.request.session['tray']:
                product = ProductModel.objects.get(id=item['item_id'], business__slug=slug)
                order_item = OrderItem(product=product, order=order, quantity=item['quantity'])
                total += order_item.total_price()
                on_the_tray.append(order_item)

            context = super(TrayListView, self).get_context_data(**kwargs)
            context['items'] = on_the_tray
            context['total'] = total
            context['order'] = order
            context['active'] = OrderModel.objects.filter(business=business, customer=customer,
                                                          status__regex='PL|S').order_by('date_ordered')
            return context
        else:
            return super(TrayListView, self).get_context_data(**kwargs)


class OrderDetailView(DetailView):
    model = OrderModel
    template_name = 'tray/order_details.html'
    context_object_name = 'order'

    def get(self, request, *args, **kwargs):

        customer = check_user(request)
        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest()

        if customer == OrderModel.objects.get(id=self.kwargs['pk']).customer:
            return super(OrderDetailView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        order_id = self.kwargs['pk']
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=order_id)
        return context


class CancelActiveOrder(View):
    def get(self, request, *args, **kwargs):

        customer = check_user(request)
        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest()

        pk = self.kwargs['pk']
        order = OrderModel.objects.get(id=pk)

        if customer == order.customer:
            if order.status == 'PL':
                order.status = 'C'
                order.save()
                messages.add_message(request, messages.INFO,
                                     "Order Cancelled")
                return redirect('tray:my_tray')
            else:
                messages.add_message(request, messages.ERROR,
                                     "Your order is already being processed or has been cancelled/paid")
                return redirect('tray:my_tray')

        else:
            return HttpResponseForbidden()


class UpdateTable(View):
    def get(self, request, *args, **kwargs):
        table_nr = self.kwargs['table_nr']
        # unlock is a number, lock is 0 because it evaluates to false
        unlock = self.kwargs['unlock']
        business_slug = self.kwargs['slug']
        customer = check_user(request)

        if customer == HttpResponseBadRequest:
            return HttpResponseBadRequest()

        try:
            table = TableModel.objects.get(business__slug=business_slug, table_nr=table_nr)
        except TableModel.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Wrong or missing table")
            self.request.session['current_order'] = None
            self.request.session['tray'] = []
            return redirect('tray:my_tray')

        if customer not in table.current_guests.all():
            messages.add_message(request, messages.ERROR, 'You are not sitting at the table currently')
            self.request.session['current_order'] = None
            self.request.session['tray'] = []
            return redirect('tray:my_tray')
        elif table.locked and unlock:
            table.locked = False
            table.save()
            messages.add_message(request, messages.INFO, 'You UNLOCKED the table')
            return redirect('tray:my_tray')
        elif not table.locked and not unlock:
            table.locked = True
            table.save()
            messages.add_message(request, messages.INFO, 'You LOCKED the table')
            return redirect('tray:my_tray')

        return redirect('tray:my_tray')
