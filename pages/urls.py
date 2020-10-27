from django.urls import path
from .views import test_view, BusinessListView, BusinessDetailView, GenerateOrder, AddToTray

urlpatterns = [
    path('', test_view, name='home'),
    path('places/', BusinessListView.as_view(), name='places'),
    path('places/<slug:slug>', BusinessDetailView.as_view(), name='place_detail'),
    path('places/<slug:slug>/generate_order', GenerateOrder.as_view(), name='generate_order'),
    path('places/<slug:slug>/add_to_tray/<int:pk>', AddToTray.as_view(), name='add_to_tray')

]
