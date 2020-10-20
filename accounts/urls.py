from django.urls import path
from .views import RegisterUserView, MyLoginView, MyLogoutView, UserDetailView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name="register"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('detail/', UserDetailView.as_view(), name='user_business_details'),

]
