from django.urls import path
from user_management.views import (
    UserRegistrationView, LoginView,
    LogoutView, CustomerCreateView,
    UserStatusListView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('customer/add/', CustomerCreateView.as_view(), name='add_customer'),
    path('status/list', UserStatusListView.as_view(), name='get_user_status'),

]
