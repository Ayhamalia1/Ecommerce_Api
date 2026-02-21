from django.urls import path 
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .serializers import CustomTokenObtainPairView  # ✅ Import custom view


urlpatterns = [
     path('register/',views.register,name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]


