import json
from random import randint

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.views.generic import View, TemplateView

from business.models import BusinessModel, ProductModel, TableModel
from .models import OrderItem, OrderModel


class TrayListView(TemplateView):
    context_object_name = 'items'
    template_name = 'tray/tray_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):

        try:
            slug = self.request.session['ordering_from']['business']
            table = self.request.session['ordering_from']['table']

            business = BusinessModel.objects.get(slug=slug)
            table = TableModel.objects.get(business=business, table_nr=table)
            customer = self.request.user

            if customer.is_authenticated:
                order = OrderModel(business=business, customer=customer, table=table, order_id=randint(1, 500),
                                   status='U')
            else:
                order = OrderModel(business=business, table=table, order_id=randint(1, 500), status='U')

            on_the_tray = []
            total = 0

            for item in self.request.session['tray']:
                product = ProductModel.objects.get(id=item['item'], business__slug=slug)
                order_item = OrderItem(product=product, order=order, quantity=item['quantity'])
                total += order_item.total_price()
                on_the_tray.append(order_item)

            context = super(TrayListView, self).get_context_data(**kwargs)
            context['items'] = on_the_tray
            context['order_status'] = order.status
            context['total'] = total
            context['active'] = OrderModel.objects.filter(business=business, customer=customer,
                                                          status__regex='PL|S').order_by('date_ordered')
            context['tray'] = self.request.session['tray']
            context['ordering_from'] = business

            return context
        except TypeError:
            return super(TrayListView, self).get_context_data(**kwargs)
        except KeyError:
            return super(TrayListView, self).get_context_data(**kwargs)


class PlaceOrder(View):
    def get(self, request, *args, **kwargs):
        slug = self.request.session['ordering_from']['business']
        table = self.request.session['ordering_from']['table']

        business = BusinessModel.objects.get(slug=slug)
        table = TableModel.objects.get(business=business, table_nr=table)
        customer = self.request.user

        if customer.is_authenticated:
            order = OrderModel.objects.create(business=business, customer=customer, table=table,
                                              order_id=randint(1, 500), status='PL')
        else:
            order = OrderModel.objects.create(business=business, table=table, order_id=randint(1, 500), status='PL')

        for item in self.request.session['tray']:
            product = ProductModel.objects.get(id=item['item'], business__slug=slug)
            OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])

        self.request.session['tray'] = []

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CancelOrder(View):
    def get(self, request, *args, **kwargs):
        if not self.kwargs['clear']:
            self.request.session['ordering_from'] = None
        self.request.session['tray'] = []
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class RemoveItemFromOrder(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        order_items = self.request.session['tray']
        for item in order_items:
            if item['item'] == pk:
                order_items.remove(item)
                break
        self.request.session['tray'] = order_items
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def update_tray(request):
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)

    product_id = int(data['id'])
    action = data['action']

    all_items = request.session['tray']
    new_value = 0

    for item in all_items:
        if item['item'] == product_id:
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
    payload = {'id': product_id, 'new_value': new_value}

    return JsonResponse(payload)


def add_remove_from_tray(request):
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)

    product_id = int(data['id'])
    action = data['action']
    all_items = request.session['tray']
    all_ids = {key['item'] for key in all_items}

    if action == 'add' and product_id not in all_ids:
        new_item = {'item': product_id, 'quantity': 1}
        all_items.append(new_item)
        request.session['tray'] = all_items
    elif action == 'remove' and product_id in all_ids:
        for item in all_items:
            if item['item'] == product_id:
                all_items.remove(item)
                break
        request.session['tray'] = all_items

    payload = {'id': product_id, 'action': action, 'status': '200'}

    return JsonResponse(payload)
