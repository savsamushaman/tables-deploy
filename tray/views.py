from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .models import OrderItem, OrderModel
from business.models import BusinessModel, ProductModel, TableModel
from accounts.models import CustomUser


class TrayListView(TemplateView):
    context_object_name = 'items'
    template_name = 'tray/tray_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        slug = self.request.session['ordering_from']['business']
        table = self.request.session['ordering_from']['table']

        business = BusinessModel.objects.get(slug=slug)
        table = TableModel.objects.get(business=business, table_nr=table)
        customer = CustomUser.objects.get(username=self.request.session['ordering_from']['customer'])

        order = OrderModel(business=business, customer=customer, table=table)

        on_the_tray = []

        for item in self.request.session['tray']:
            product = ProductModel.objects.get(id=item, business__slug=slug)
            on_the_tray.append(OrderItem(product=product, order=order))

        context = super(TrayListView, self).get_context_data(**kwargs)
        context['items'] = on_the_tray
        return context


class PlaceOrderView(View):
    def get(self, request, *args, **kwargs):
        slug = self.request.session['ordering_from']['business']
        table = self.request.session['ordering_from']['table']

        business = BusinessModel.objects.get(slug=slug)
        table = TableModel.objects.get(business=business, table_nr=table)
        customer = CustomUser.objects.get(username=self.request.session['ordering_from']['customer'])

        order = OrderModel.objects.create(business=business, customer=customer, table=table)

        for item in self.request.session['tray']:
            product = ProductModel.objects.get(id=item, business__slug=slug)
            OrderItem.objects.create(product=product, order=order)

        self.request.session['tray'] = []

        return redirect('my_tray')
