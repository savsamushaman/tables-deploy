from django.urls import path
from .views import TrayListView, PlaceOrderView

urlpatterns = [
    path('my_tray/', TrayListView.as_view(), name='my_tray'),
    path('place_order/', PlaceOrderView.as_view(), name='place_order')
]
