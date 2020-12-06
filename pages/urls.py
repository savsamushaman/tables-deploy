from django.urls import path

from .views import PlaceListView, PlaceDetailView, AboutView, filter_places

app_name = 'pages'

urlpatterns = [

    path('', PlaceListView.as_view(), name='places'),
    path('places/filter/', filter_places, name='filter'),
    path('places/<slug:slug>', PlaceDetailView.as_view(), name='place_detail'),
    path('about/', AboutView.as_view(), name='home'),

]
