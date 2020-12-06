import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.generic import ListView, DetailView, TemplateView

from business.models import BusinessModel, ProductModel, ProductCategory, TableModel
from .filters import BusinessFilter


class AboutView(TemplateView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        a = request.session.get('tray', [])
        b = request.session.get('current_order', None)
        print(a)
        print(b)
        return super(AboutView, self).get(request, *args, **kwargs)


class PlaceListView(ListView):
    model = BusinessModel
    template_name = 'pages/places_list.html'
    context_object_name = 'businesses'
    my_filter = BusinessFilter

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PlaceListView, self).get_context_data(**kwargs)

        context['current_order'] = self.request.session.get('current_order', '')

        if self.request.GET:
            result_filter = self.my_filter(self.request.GET, queryset=context['businesses'])
            context['filter'] = result_filter
            context['businesses'] = result_filter.qs
        else:
            if hasattr(self.request.user, 'country'):
                data = self.request.GET.copy()
                data['country'] = self.request.user.country

                result_filter = self.my_filter(data, queryset=context['businesses'])
                context['filter'] = result_filter
                context['businesses'] = result_filter.qs.filter(country=self.request.user.country)
            else:
                result_filter = self.my_filter(request=self.request.GET, queryset=context['businesses'])
                context['filter'] = result_filter
                context['businesses'] = result_filter.qs

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
        context['tables'] = TableModel.objects.filter(business=kwargs['object'], deleted=False)
        context['categories'] = ProductCategory.objects.filter(business=kwargs['object'], deleted=False)
        context['products'] = ProductModel.objects.filter(business=kwargs['object'], deleted=False)
        context['current_order'] = self.request.session.get('current_order', '')

        return context


def filter_places(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed('POST')

    data = json.loads(request.body)
    search_value = data['search_value']
    results = BusinessModel.objects.filter(business_name__contains=search_value, is_active=True).values(
        'business_name') | \
              BusinessModel.objects.filter(displayed_address__contains=search_value, is_active=True).values(
                  'business_name') | \
              BusinessModel.objects.filter(category__category_name__contains=search_value, is_active=True).values(
                  'business_name')

    results = [result['business_name'] for result in results]
    payload = {'results': results}

    return JsonResponse(payload)
