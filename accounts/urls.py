from django.urls import path
from .views import RegisterUserView, MyLoginView, MyLogoutView, UserDetailView, BusinessEditView, ProductEditView, \
    CreateProductView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name="register"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('detail/', UserDetailView.as_view(), name='user_details'),
    path('detail/<slug:slug>/update/', BusinessEditView.as_view(), name='business_update'),
    path('detail/<slug:slug>/update/products/<int:pk>', ProductEditView.as_view(), name='update_product'),
    path('detail/<slug:slug>/update/products/create', CreateProductView.as_view(), name='create_product')

]
