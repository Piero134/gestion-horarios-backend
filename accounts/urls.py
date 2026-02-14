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
]
