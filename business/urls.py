from django.urls import path

from .views import CreateBusinessView, BusinessEditView, ProductEditView, CreateProductView, ProductListView, \
    TableListView, CreateTableView, TableEditView, ProductDeleteView, TableDeleteView, FeedView, ProcessOrder, \
    BusinessListView, ReturnOrders

app_name = 'owned'

urlpatterns = [
    path('', BusinessListView.as_view(), name='owned_list'),
    path('active_orders/', ReturnOrders.as_view(), name='return_orders'),
    path('create_business/', CreateBusinessView.as_view(), name='create_business'),
    path('<slug:slug>/update/', BusinessEditView.as_view(), name='business_update'),
    path('<slug:slug>/update/products/', ProductListView.as_view(), name='products_list'),
    path('<slug:slug>/update/products/create', CreateProductView.as_view(), name='create_product'),
    path('<slug:slug>/update/products/<int:pk>', ProductEditView.as_view(), name='update_product'),
    path('<slug:slug>/update/products/delete/<int:pk>', ProductDeleteView.as_view(), name='delete_product'),
    path('<slug:slug>/update/tables/', TableListView.as_view(), name='tables_list'),
    path('<slug:slug>/update/tables/create', CreateTableView.as_view(), name='create_table'),
    path('<slug:slug>/update/tables/<int:pk>', TableEditView.as_view(), name='update_table'),
    path('<slug:slug>/update/tables/delete/<int:pk>', TableDeleteView.as_view(), name='delete_table'),
    path('<slug:slug>/feed/', FeedView.as_view(), name='feed'),
    path('<slug:slug>/feed/<int:pk>', ProcessOrder.as_view(), name='process_order'),
]
