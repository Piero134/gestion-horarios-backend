from django.contrib import admin
from django.urls import path,include
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('',login_page,name='login_page'),
    path('register/',register_page,name='register_page'),
]
