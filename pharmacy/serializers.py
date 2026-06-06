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
# STAFF (SECURE + READABLE)
# =========================
class PharmacyStaffSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
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
# RESERVATION (CORE SYSTEM)
# =========================
class ReservationSerializer(serializers.ModelSerializer):

    # readable fields for frontend
    user_name = serializers.ReadOnlyField(source='user.username')
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')
    medicine_name = serializers.ReadOnlyField(source='medicine.name')

    class Meta:
        model = Reservation
        fields = '__all__'

    # SECURITY FIX: prevent frontend from faking user
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)