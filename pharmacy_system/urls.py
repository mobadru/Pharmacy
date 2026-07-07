from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from pharmacy.views import CustomTokenObtainPairView  # IMPORTANT FIX

urlpatterns = [
    path("admin/", admin.site.urls),

    # AUTH (ONLY HERE)
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # APP
    path("api/", include("pharmacy.urls")),
]