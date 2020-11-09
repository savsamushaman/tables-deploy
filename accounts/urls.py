from django.urls import path
from .views import RegisterUserView, MyLoginView, MyLogoutView, UserDetailView, CreateBusinessView, BusinessEditView, \
    ProductEditView, \
    CreateProductView, ProductListView, TableListView, CreateTableView, TableEditView, ProductDeleteView, \
    TableDeleteView, FeedView, ProcessOrder

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name="register"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('detail/', UserDetailView.as_view(), name='user_details'),
    path('detail/create_business', CreateBusinessView.as_view(), name='create_business'),
    path('detail/<slug:slug>/update/', BusinessEditView.as_view(), name='business_update'),
    path('detail/<slug:slug>/update/products/', ProductListView.as_view(), name='products_list'),
    path('detail/<slug:slug>/update/products/create', CreateProductView.as_view(), name='create_product'),
    path('detail/<slug:slug>/update/products/<int:pk>', ProductEditView.as_view(), name='update_product'),
    path('detail/<slug:slug>/update/products/delete/<int:pk>', ProductDeleteView.as_view(), name='delete_product'),
    path('detail/<slug:slug>/update/tables/', TableListView.as_view(), name='tables_list'),
    path('detail/<slug:slug>/update/tables/create', CreateTableView.as_view(), name='create_table'),
    path('detail/<slug:slug>/update/tables/<int:pk>', TableEditView.as_view(), name='update_table'),
    path('detail/<slug:slug>/update/tables/delete/<int:pk>', TableDeleteView.as_view(), name='delete_table'),
    path('detail/<slug:slug>/feed/', FeedView.as_view(), name='feed'),
    path('detail/<slug:slug>/feed/<int:pk>', ProcessOrder.as_view(), name='process_order'),

]
