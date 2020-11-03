from django.urls import path
from .views import TrayListView, PlaceOrder, RemoveItemFromOrder, CancelOrder, update_tray

app_name = 'tray'

urlpatterns = [
    path('', TrayListView.as_view(), name='my_tray'),
    path('place_order/', PlaceOrder.as_view(), name='place_order'),
    path('remove_item/<int:pk>', RemoveItemFromOrder.as_view(), name='remove_item'),
    path('cancel_order/<int:clear>', CancelOrder.as_view(), name='cancel_order'),
    path('update_tray/', update_tray, name='update_tray')

]
