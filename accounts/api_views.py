from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status,authentication, permissions 
from django.contrib.auth.models import User
from .serializers import *
from django.contrib.auth import logout

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        username = request.data.get('username',"").strip()
        password = request.data.get('password',"")
        email = request.data.get('email',"").strip()

        if not username or not password or not email:
            return Response(
                {"error":"Todos los campos deben estar llenos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password)<8:
            return Response(
                {"error":"La cantidad de caracteres de la contraseña debe ser mayor a 8"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username = username).exists():
            return Response(
                {"error":"El nombre de usuario ya existe, use otro"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {"error":"El email ya existe, use otro"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(
            username = username,
            password = password,
            email = email
        )

        serializer = UserSerializer(user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        
class LogoutApiView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.AllowAny]
    def post(self,request):
        logout(request)
        return Response(
            {"message":"Sesión cerrada con éxito"},
            status = status.HTTP_200_OK
        )