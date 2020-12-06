from django.urls import path

from .views import TrayListView, GenerateOrder, PlaceOrder, RemoveItemFromOrder, CancelOrder, update_tray, \
    add_remove_from_tray, OrderDetailView, CancelActiveOrder, UpdateTable

app_name = 'tray'

urlpatterns = [
    path('', TrayListView.as_view(), name='my_tray'),
    path('order_detail/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('generate_order/<slug:place>/<int:table_nr>', GenerateOrder.as_view(), name='generate_order'),
    path('place_order/', PlaceOrder.as_view(), name='place_order'),
    path('cancel_order/<int:clear>', CancelOrder.as_view(), name='cancel_order'),
    path('cancel_active_order/<int:pk>', CancelActiveOrder.as_view(), name='cancel_active_order'),
    path('add_remove/', add_remove_from_tray, name='add_remove'),
    path('remove_item/<int:pk>', RemoveItemFromOrder.as_view(), name='remove_item'),
    path('update_tray/', update_tray, name='update_tray'),
    path('update_table/<slug:slug>/<int:table_nr>/<int:unlock>', UpdateTable.as_view(), name='update_table')

]
