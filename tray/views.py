import json


from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from accounts.models import CustomUser
from business.models import BusinessModel, ProductModel, TableModel
from .models import OrderItem, OrderModel


class GenerateOrder(View):

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['place']
        table = TableModel.objects.get(table_nr=self.kwargs['table_nr'], business__slug=slug)
        order = {'customer': str(self.request.user), 'business': slug, 'table': table.table_nr}
        self.request.session['current_order'] = order
        self.request.session['tray'] = []
        return redirect('pages:place_detail', slug=slug)


class CancelOrder(View):
    def get(self, request, *args, **kwargs):

        try:
            redirect_to = self.request.session['current_order']['business']
        except TypeError:
            return HttpResponseBadRequest

        if not self.kwargs['clear']:
            self.request.session['current_order'] = None
            return redirect('pages:place_detail', slug=redirect_to)
        self.request.session['tray'] = []
        return redirect('tray:my_tray')


class PlaceOrder(View):
    def get(self, request, *args, **kwargs):
        try:
            slug = self.request.session['current_order']['business']
            table = self.request.session['current_order']['table']
            if self.request.user.is_authenticated:
                customer = self.request.user
            else:
                if self.request.COOKIES['device']:
                    device = self.request.COOKIES['device']
                    customer, created = CustomUser.objects.get_or_create(device=device)
                else:
                    return HttpResponseBadRequest
            business = BusinessModel.objects.get(slug=slug)
            table = TableModel.objects.get(business=business, table_nr=table)
            order = OrderModel.objects.create(business=business, customer=customer, table=table, status='PL')

            total = 0

            for item in self.request.session['tray']:
                product = ProductModel.objects.get(id=item['item_id'], business__slug=slug)
                order_item = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])
                total += order_item.total_price()

            order.total = total

            self.request.session['tray'] = []

            return redirect('tray:my_tray')

        except KeyError:
            return HttpResponseBadRequest


class RemoveItemFromOrder(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        order_items = self.request.session['tray']
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

        all_items = request.session['tray']
        new_value = 0

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
        return HttpResponseBadRequest


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
        return HttpResponseBadRequest

    return response


class TrayListView(TemplateView):
    context_object_name = 'items'
    template_name = 'tray/tray_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        try:
            slug = self.request.session['current_order']['business']
            table = self.request.session['current_order']['table']

            business = BusinessModel.objects.get(slug=slug)
            table = TableModel.objects.get(business=business, table_nr=table)

            if self.request.user.is_authenticated:
                customer = self.request.user
            else:
                if self.request.COOKIES['device']:
                    device = self.request.COOKIES['device']
                    customer, created = CustomUser.objects.get_or_create(device=device)
                else:
                    return HttpResponseBadRequest

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

        except TypeError:
            return super(TrayListView, self).get_context_data(**kwargs)
        except KeyError:
            return super(TrayListView, self).get_context_data(**kwargs)
