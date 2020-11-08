from random import choice

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView

from business.models import BusinessModel, ProductModel, TableModel, ProductCategory


def test_view(request):
    template_name = 'pages/index.html'
    a = request.session.get('tray', 'Nay')
    b = request.session.get('ordering_from', 'None')
    print(a)
    print(b)
    return render(request, template_name, {})


class BusinessListView(ListView):
    model = BusinessModel
    template_name = 'pages/places_list.html'
    context_object_name = 'businesses'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BusinessListView, self).get_context_data(**kwargs)
        context['current_order'] = self.request.session.get('ordering_from', '')
        return context


class BusinessDetailView(DetailView):
    model = BusinessModel
    template_name = 'pages/place_details.html'
    context_object_name = 'place'

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailView, self).get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(business=kwargs['object'])
        context['products'] = ProductModel.objects.filter(business=kwargs['object'])
        context['ordering_from'] = self.request.session.get('ordering_from', '')
        context['tray'] = self.request.session.get('tray', '')
        prod = [item['item'] for item in context['tray']]
        context['prod'] = prod

        return context


class GenerateOrder(View):

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        tables = TableModel.objects.filter(business__slug=slug)
        table = choice(tables)
        order = {'customer': str(self.request.user), 'business': slug, 'table': table.table_nr}
        self.request.session['ordering_from'] = order
        self.request.session['tray'] = []
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
