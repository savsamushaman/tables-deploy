from django.urls import path

from .views import RegisterUserView, MyLoginView, MyLogoutView, UserDetailView, CustomPasswordResetView, \
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetComplete, UpdateUserView, \
    ChangePasswordView, ChangePasswordDoneView, activate_user, InvitationsListView, InvitationAction

app_name = 'accounts'

urlpatterns = [
    path('', UserDetailView.as_view(), name='user_details'),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('activate/<uidb64>/<token>/', activate_user, name="activate"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', CustomPasswordResetComplete.as_view(), name='password_reset_complete'),
    path('change_userdetails/<slug:slug>/', UpdateUserView.as_view(), name='update_user'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('change_password/done/', ChangePasswordDoneView.as_view(), name='change_password_done'),
    path('invitations/', InvitationsListView.as_view(), name='invitations_list'),
    path('invitations/<int:pk>/<int:action>', InvitationAction.as_view(), name='invitation_action')

]
