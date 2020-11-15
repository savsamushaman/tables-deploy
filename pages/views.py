import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q

from business.models import BusinessModel, ProductModel, ProductCategory, TableModel


def test_view(request):
    template_name = 'pages/index.html'
    a = request.session.get('tray', [])
    b = request.session.get('current_order', None)
    print(a)
    print(b)
    return render(request, template_name, {})


class PlaceListView(ListView):
    model = BusinessModel
    template_name = 'pages/places_list.html'
    context_object_name = 'businesses'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PlaceListView, self).get_context_data(**kwargs)
        context['current_order'] = self.request.session.get('current_order', '')
        try:
            if self.request.user.country:
                context['businesses'] = BusinessModel.objects.filter(country=self.request.user.country)
            else:
                context['businesses'] = BusinessModel.objects.all()
            return context
        except AttributeError:
            return context


class PlaceDetailView(DetailView):
    model = BusinessModel
    template_name = 'pages/place_details.html'
    context_object_name = 'place'

    def get_context_data(self, **kwargs):
        context = super(PlaceDetailView, self).get_context_data(**kwargs)

        try:
            on_the_tray = [item['item_id'] for item in self.request.session.get('tray', None)]
        except TypeError:
            on_the_tray = []

        context['on_the_tray'] = on_the_tray
        context['tables'] = TableModel.objects.filter(business=kwargs['object'])
        context['categories'] = ProductCategory.objects.filter(business=kwargs['object'])
        context['products'] = ProductModel.objects.filter(business=kwargs['object'])
        context['current_order'] = self.request.session.get('current_order', '')

        return context


def filter_places(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed('POST')

    data = json.loads(request.body)
    results = BusinessModel.objects.filter(business_name__contains=data['search_value']).values(
        'business_name') | BusinessModel.objects.filter(
        displayed_address__contains=data['search_value']).values('business_name')

    results = [result['business_name'] for result in results]
    payload = {'results': results}

    return JsonResponse(payload)
