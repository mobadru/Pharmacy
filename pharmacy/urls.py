from django.urls import path
from .views import (
    manage_pharmacy,
    manage_staff,
    manage_medicine,
    manage_stock,
    manage_reservation,
    approve_reservation,
    reject_reservation
)

urlpatterns = [
    # PHARMACY
    path('pharmacies/', manage_pharmacy),
    path('pharmacies/<int:pk>/', manage_pharmacy),

    # STAFF
    path('staff/', manage_staff),
    path('staff/<int:pk>/', manage_staff),

    # MEDICINES
    path('medicines/', manage_medicine),
    path('medicines/<int:pk>/', manage_medicine),

    # STOCK
    path('stocks/', manage_stock),
    path('stocks/<int:pk>/', manage_stock),

    # RESERVATIONS
    path('reservations/', manage_reservation),
    path('reservations/<int:pk>/', manage_reservation),

    # WORKFLOW
    path('reservations/<int:pk>/approve/', approve_reservation),
    path('reservations/<int:pk>/reject/', reject_reservation),
]