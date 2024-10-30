"""
URL configuration for busSchedulingServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from .views import LoginAPIView, ProtectedView,ChangePasswordView,ResetPasswordRequestview,ResetPasswordView,GetUserProfileDetails,UpdateUserProfile
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginAPIView.as_view(), name='user login'),
    path('changePassword/', ChangePasswordView.as_view(), name='change password'),
    path('resetPasswordRequest/', ResetPasswordRequestview.as_view(), name='reset password request'),
    path('resetPassword/', ResetPasswordView.as_view(), name='reset password'),
    path('getUserDetails/',GetUserProfileDetails.as_view(),name='get user detaials'),
     path('updateUserProfile/',UpdateUserProfile.as_view(),name='update user profile')
]
