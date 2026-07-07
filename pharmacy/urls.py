from django.urls import path
from .views import (
    manage_pharmacy,
    manage_staff,
    manage_product,
    manage_stock,
    manage_reservation,
    approve_reservation,
    reject_reservation,
)


urlpatterns = [
    path("pharmacies/", manage_pharmacy),
    path("pharmacies/<int:pk>/", manage_pharmacy),

    path("staff/", manage_staff),
    path("staff/<int:pk>/", manage_staff),

    path("products/", manage_product),
    path("products/<int:pk>/", manage_product),

    path("stocks/", manage_stock),
    path("stocks/<int:pk>/", manage_stock),

    path("reservations/", manage_reservation),
    path("reservations/<int:pk>/", manage_reservation),

    path("reservations/<int:pk>/approve/", approve_reservation),
    path("reservations/<int:pk>/reject/", reject_reservation),
    
]