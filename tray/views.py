from random import randint

from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView

from business.models import BusinessModel, ProductModel, TableModel
from .models import OrderItem, OrderModel


class TrayListView(TemplateView):
    context_object_name = 'items'
    template_name = 'tray/tray_list.html'

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
                product = ProductModel.objects.get(id=item, business__slug=slug)
                order_item = OrderItem(product=product, order=order)
                total += order_item.price()
                on_the_tray.append(order_item)

            context = super(TrayListView, self).get_context_data(**kwargs)
            context['items'] = on_the_tray
            context['order_status'] = order.status
            context['total'] = total
            context['active'] = OrderModel.objects.filter(business=business, customer=customer,
                                                          status__regex='PL|S').order_by('date_ordered')
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
            product = ProductModel.objects.get(id=item, business__slug=slug)
            OrderItem.objects.create(product=product, order=order)

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
        order_items.remove(pk)
        self.request.session['tray'] = order_items
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
