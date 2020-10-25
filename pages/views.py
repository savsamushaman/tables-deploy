from django.shortcuts import render
from django.views.generic import ListView, DetailView
from business.models import BusinessModel, ProductModel


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
        print(self.request)
        return super(BusinessDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailView, self).get_context_data(**kwargs)
        context['products'] = ProductModel.objects.filter(business=kwargs['object'])
        return context
