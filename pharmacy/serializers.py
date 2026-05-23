from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Pharmacy, PharmacyStaff, Medicine, Stock, Reservation


# =========================
# USER SERIALIZER
# =========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# =========================
# PHARMACY
# =========================
class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'


# =========================
# STAFF
# =========================
class PharmacyStaffSerializer(serializers.ModelSerializer):

    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')

    class Meta:
        model = PharmacyStaff
        fields = '__all__'


# =========================
# MEDICINE
# =========================
class MedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = '__all__'


# =========================
# STOCK
# =========================
class StockSerializer(serializers.ModelSerializer):

    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')
    medicine_name = serializers.ReadOnlyField(source='medicine.name')

    class Meta:
        model = Stock
        fields = '__all__'


# =========================
# RESERVATION (CORE LOGIC)
# =========================
class ReservationSerializer(serializers.ModelSerializer):

    user_name = serializers.ReadOnlyField(source='user.username')
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')
    medicine_name = serializers.ReadOnlyField(source='medicine.name')

    class Meta:
        model = Reservation
        fields = '__all__'