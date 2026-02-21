<<<<<<< HEAD
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home
from .forms import LoginForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=LoginForm
    ), name='login'),
    path('', home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
=======
from django.contrib import admin
from django.urls import path,include
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('',login_page,name='login_page'),
    path('register/',register_page,name='register_page'),
    path('dashboard/',dashboard_page,name='dashboard_page'),
>>>>>>> 71224ecb86f8f8c385092b501f3124b34fd8718b
]
