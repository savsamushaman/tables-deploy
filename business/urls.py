from django.urls import path

from .views import CreateBusinessView, BusinessEditView, ProductEditView, CreateProductView, ProductListView, \
    TableListView, CreateTableView, TableEditView, ProductDeleteView, TableDeleteView, FeedView, ProcessOrder, \
    BusinessListView, ReturnOrders, CreateMenuPoint, MenuPointListView, MenuPointEditView, MenuPointDelete, \
    BusinessDeleteView

app_name = 'owned'

urlpatterns = [
    path('', BusinessListView.as_view(), name='owned_list'),
    path('active_orders/', ReturnOrders.as_view(), name='return_orders'),
    path('create_business/', CreateBusinessView.as_view(), name='create_business'),
    path('delete_business/<slug:slug>', BusinessDeleteView.as_view(), name='delete_business'),
    path('<slug:slug>/update/', BusinessEditView.as_view(), name='business_update'),
    path('<slug:slug>/update/products/', ProductListView.as_view(), name='products_list'),
    path('<slug:slug>/update/products/create', CreateProductView.as_view(), name='create_product'),
    path('<slug:slug>/update/products/<int:pk>', ProductEditView.as_view(), name='update_product'),
    path('<slug:slug>/update/products/delete/<int:pk>', ProductDeleteView.as_view(), name='delete_product'),
    path('<slug:slug>/update/tables/', TableListView.as_view(), name='tables_list'),
    path('<slug:slug>/update/tables/create', CreateTableView.as_view(), name='create_table'),
    path('<slug:slug>/update/tables/<int:pk>', TableEditView.as_view(), name='update_table'),
    path('<slug:slug>/update/tables/delete/<int:pk>', TableDeleteView.as_view(), name='delete_table'),
    path('<slug:slug>/update/menupoints/', MenuPointListView.as_view(), name='menupoints_list'),
    path('<slug:slug>/update/menupoints/create', CreateMenuPoint.as_view(), name='create_menu_point'),
    path('<slug:slug>/update/menupoints/<int:pk>', MenuPointEditView.as_view(), name='update_menupoint'),
    path('<slug:slug>/update/menupoints/delete/<int:pk>', MenuPointDelete.as_view(), name='delete_menupoint'),

    path('<slug:slug>/feed/', FeedView.as_view(), name='feed'),
    path('<slug:slug>/feed/<int:pk>', ProcessOrder.as_view(), name='process_order'),
]
