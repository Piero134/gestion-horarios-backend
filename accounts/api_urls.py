from django.contrib import admin
from django.urls import path,include
from .api_views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'api_accounts'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view() ,name="login"),
    path('register/',RegisterAPIView.as_view(),name="register"),
    path('logout/',LogoutApiView.as_view(),name='logout'),
]