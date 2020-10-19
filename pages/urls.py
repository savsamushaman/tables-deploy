from django.urls import path
from .views import test_view, BusinessListView

urlpatterns = [
    path('', test_view, name='home'),
    path('places/', BusinessListView.as_view(), name='places')

]
