from django.contrib import admin
from .models import (
    UserProfile,
    Pharmacy,
    PharmacyStaff,
    Product,
    Stock,
    Reservation,
)


# =====================================
# USER PROFILE
# =====================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "phone",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
    )

    list_filter = (
        "role",
    )


# =====================================
# PHARMACY
# =====================================
@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location_name",
        "phone",
        "license_number",
    )

    search_fields = (
        "name",
        "location_name",
        "license_number",
    )


# =====================================
# PHARMACY STAFF
# =====================================
@admin.register(PharmacyStaff)
class PharmacyStaffAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "pharmacy",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "pharmacy",
    )


# =====================================
# PRODUCT
# =====================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand",
        "category",
        "unit",
        "requires_prescription",
    )

    search_fields = (
        "name",
        "brand",
    )

    list_filter = (
        "category",
        "unit",
        "requires_prescription",
    )


# =====================================
# STOCK
# =====================================
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    list_display = (
        "pharmacy",
        "product",
        "quantity",
        "batch_number",
        "expiry_date",
    )

    search_fields = (
        "product__name",
        "brand",
        "pharmacy__name",
    )

    list_filter = (
        "pharmacy",
        "product__category",
    )


# =====================================
# RESERVATION
# =====================================
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "pharmacy",
        "quantity",
        "status",
        "reservation_date",
        "processed_by",
    )

    search_fields = (
        "user__username",
        "product__name",
        "pharmacy__name",
    )

    list_filter = (
        "status",
        "pharmacy",
    )

    readonly_fields = (
        "reservation_date",
    )