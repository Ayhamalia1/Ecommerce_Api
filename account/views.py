from django.shortcuts import render
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status




# Create your views here.
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data =request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"User created sucessfully"},status=status.HTTP_201_CREATED)
    return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
