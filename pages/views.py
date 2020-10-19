from django.shortcuts import render
from django.views.generic import ListView
from business.models import BusinessModel


def test_view(request):
    template_name = 'pages/index.html'
    return render(request, template_name, {})


class BusinessListView(ListView):
    model = BusinessModel
    template_name = 'pages/list.html'
    context_object_name = 'businesses'



