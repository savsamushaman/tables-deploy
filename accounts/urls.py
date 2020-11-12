from django.urls import path
from .views import RegisterUserView, MyLoginView, MyLogoutView, UserDetailView

app_name = 'accounts'

urlpatterns = [
    path('', UserDetailView.as_view(), name='user_details'),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),

]
