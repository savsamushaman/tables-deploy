import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from business.models import BusinessModel, ProductModel, ProductCategory


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


def filter_places(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed('POST')

    data = json.loads(request.body)
    results = BusinessModel.objects.filter(business_name__contains=data['search_value']).values('business_name')
    results = [result['business_name'] for result in results]
    payload = {'results': results}

    return JsonResponse(payload)
