from django.shortcuts import render
from django.views.generic import ListView, View, TemplateView
from .models import OrderItem


class TrayListView(ListView):
    model = OrderItem
    context_object_name = 'items'
    template_name = 'tray/tray_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TrayListView, self).get_context_data(**kwargs)
        context['items'] = OrderItem.objects.filter(order__customer=self.request.user)
        return context
