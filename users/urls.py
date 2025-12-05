from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, VerifyEmailView,
    ResendVerificationView, PasswordResetRequestView,
    PasswordResetConfirmView, ProfileView, ChangePasswordView,
    DeactivateAccountView, UserListView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email verification
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    
    # Password management
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Profile & Account
    path('profile/', ProfileView.as_view(), name='profile'),
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate'),
    path('list/', UserListView.as_view(), name='user_list'),
]
