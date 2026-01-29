from django.shortcuts import render

# Create your views here.
def login_page(request):
    return render(request,'login.html')

def register_page(request):
    return render(request,'register.html')

def dashboard_page(request):
    return render(request,'dashboard.html')
