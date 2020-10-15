from django.urls import path
from .views import RegisterUserView, MyLoginView, MyLogoutView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name="register"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout')
]
