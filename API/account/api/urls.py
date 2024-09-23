from rest_framework.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify/', VerifyOTPAPI.as_view(), name='verify-email'),
    path('login/' , LoginAPI.as_view() , name = 'login'),
    path('logout/' , LogoutAPI.as_view() , name = 'logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-pass-otp/' , ResetPasswordOTP_API.as_view() , name = 'login'),
    path('reset-pass/' , ResetPasswordAPI.as_view() , name = 'login'),
]