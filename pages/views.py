from random import randint, choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from business.models import BusinessModel, ProductModel, TableModel
from tray.models import OrderModel


def test_view(request):
    template_name = 'pages/index.html'
    return render(request, template_name, {})


class BusinessListView(ListView):
    model = BusinessModel
    template_name = 'pages/list.html'
    context_object_name = 'businesses'


class BusinessDetailView(DetailView):
    model = BusinessModel
    template_name = 'pages/place_details.html'
    context_object_name = 'place'

    def get(self, request, *args, **kwargs):
        return super(BusinessDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailView, self).get_context_data(**kwargs)
        context['products'] = ProductModel.objects.filter(business=kwargs['object'])
        context['ordering_from'] = self.request.session.get('ordering_from', '')
        return context


class GenerateOrder(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        tables = TableModel.objects.filter(business__slug=slug)
        table = choice(tables)
        business = BusinessModel.objects.get(slug=slug)
        order = OrderModel.objects.create(customer=request.user, business=business, order_id=str(randint(5, 500)),
                                          table=table)
        self.request.session['ordering_from'] = model_to_dict(order)['business']
        return redirect('place_detail', slug=slug)
