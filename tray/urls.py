from django.urls import path
from .views import TrayListView

urlpatterns = [
    path('my_tray/', TrayListView.as_view(), name='my_tray')
]
