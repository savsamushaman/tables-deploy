from django.urls import path
from .views import test_view, BusinessListView, BusinessDetailView

urlpatterns = [
    path('', test_view, name='home'),
    path('places/', BusinessListView.as_view(), name='places'),
    path('places/<slug:slug>', BusinessDetailView.as_view(), name='place_detail')

]
