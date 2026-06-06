from django.contrib import admin
from .models import Pharmacy, PharmacyStaff, Medicine, Stock, Reservation


# =========================
# PHARMACY
# =========================
@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_name', 'phone', 'license_number')
    search_fields = ('name', 'location_name', 'license_number')


# =========================
# STAFF
# =========================
@admin.register(PharmacyStaff)
class PharmacyStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'pharmacy')
    search_fields = ('user__username', 'user__email')
    list_filter = ('pharmacy',)

# =========================
# MEDICINE
# =========================
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'requires_prescription')
    search_fields = ('name', 'brand')
    list_filter = ('requires_prescription',)


# =========================
# STOCK
# =========================
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'medicine', 'quantity')
    search_fields = ('medicine__name', 'pharmacy__name')
    list_filter = ('pharmacy',)


# =========================
# RESERVATION
# =========================
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'medicine', 'pharmacy', 'status', 'reservation_date')
    search_fields = ('user__username', 'medicine__name')
    list_filter = ('status', 'pharmacy')