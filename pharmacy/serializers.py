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
        read_only_fields = ['pharmacy']

    def create(self, validated_data):

        request = self.context['request']

        pharmacy = request.user.staff_profile.pharmacy

        validated_data['pharmacy'] = pharmacy

        return Stock.objects.create(**validated_data)


# =========================
# RESERVATION (CORE SYSTEM)
# =========================
class ReservationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="user.username", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    pharmacy_name = serializers.CharField(source="pharmacy.name", read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"

    # SECURITY FIX: prevent frontend from faking user
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)