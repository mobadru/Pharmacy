from django.urls import path

from .views import (
    manage_pharmacy,
    manage_staff,
    manage_product,
    manage_stock,
    manage_reservation,
    approve_reservation,
    reject_reservation,
    register_patient,
    forgot_password,
    profile,
    change_password,
)



urlpatterns = [

    # ==========================
    # PATIENT AUTH
    # ==========================

    path(
        "register/",
        register_patient,
        name="patient_register"
    ),



    # ==========================
    # PHARMACY
    # ==========================

    path(
        "pharmacies/",
        manage_pharmacy
    ),

    path(
        "pharmacies/<int:pk>/",
        manage_pharmacy
    ),



    # ==========================
    # STAFF
    # ==========================

    path(
        "staff/",
        manage_staff
    ),

    path(
        "staff/<int:pk>/",
        manage_staff
    ),



    # ==========================
    # PRODUCTS
    # ==========================

    path(
        "products/",
        manage_product
    ),

    path(
        "products/<int:pk>/",
        manage_product
    ),



    # ==========================
    # STOCK
    # ==========================

    path(
        "stocks/",
        manage_stock
    ),

    path(
        "stocks/<int:pk>/",
        manage_stock
    ),



    # ==========================
    # RESERVATIONS
    # ==========================

    path(
        "reservations/",
        manage_reservation
    ),

    path(
        "reservations/<int:pk>/",
        manage_reservation
    ),



    path(
        "reservations/<int:pk>/approve/",
        approve_reservation
    ),


    path(
        "reservations/<int:pk>/reject/",
        reject_reservation
    ),
    path(
        "profile/",
        profile,
        name="profile",
    ),

    path(
        "change-password/",
        change_password,
        name="change-password"
    ),

    path(
    "forgot-password/",
    forgot_password,
    name="forgot_password"
),

]