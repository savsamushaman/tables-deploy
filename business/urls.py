from django.urls import path
from .views import CreateBusinessView

urlpatterns = [
    path('create/', CreateBusinessView.as_view(), name='create_business')
]
