from django.urls import path
from .views import TrayListView, GenerateOrder, PlaceOrder, RemoveItemFromOrder, CancelOrder, update_tray, \
    add_remove_from_tray

app_name = 'tray'

urlpatterns = [
    path('', TrayListView.as_view(), name='my_tray'),
    path('generate_order/<slug:slug>', GenerateOrder.as_view(), name='generate_order'),
    path('place_order/', PlaceOrder.as_view(), name='place_order'),
    path('cancel_order/<int:clear>', CancelOrder.as_view(), name='cancel_order'),
    path('add_remove/', add_remove_from_tray, name='add_remove'),
    path('remove_item/<int:pk>', RemoveItemFromOrder.as_view(), name='remove_item'),
    path('update_tray/', update_tray, name='update_tray'),
    # updates quantity

]
