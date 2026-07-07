from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date

from .models import (
    UserProfile,
    Pharmacy,
    PharmacyStaff,
    Product,
    Stock,
    Reservation,
)

# =====================================
# HELPERS
# =====================================

def get_profile(user):
    return getattr(user, "profile", None)


def is_staff(user):
    profile = get_profile(user)
    return profile and profile.role == "staff"


def is_patient(user):
    profile = get_profile(user)
    return profile and profile.role == "patient"


def get_staff_pharmacy(user):
    try:
        return user.pharmacystaff.pharmacy
    except:
        return None


# =====================================
# USER
# =====================================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, role="patient")

        return user


# =====================================
# USER PROFILE
# =====================================
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


# =====================================
# PHARMACY
# =====================================
class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"


# =====================================
# PHARMACY STAFF
# =====================================
class PharmacyStaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pharmacy_name = serializers.ReadOnlyField(source="pharmacy.name")

    class Meta:
        model = PharmacyStaff
        fields = "__all__"


# =====================================
# PRODUCT
# =====================================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


# =====================================
# STOCK (FULL UPGRADE)
# =====================================
class StockSerializer(serializers.ModelSerializer):

    pharmacy_name = serializers.ReadOnlyField(source="pharmacy.name")
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = Stock
        fields = "__all__"
        read_only_fields = ["pharmacy"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        # check staff
        profile = getattr(user, "profile", None)
        if not profile or profile.role != "staff":
            raise serializers.ValidationError("Only staff can add stock")

        # get pharmacy safely
        staff = PharmacyStaff.objects.filter(user=user).first()

        if not staff:
            raise serializers.ValidationError("Staff not linked to pharmacy")

        pharmacy = staff.pharmacy

        # 🔥 FORCE pharmacy injection (VERY IMPORTANT)
        validated_data["pharmacy"] = pharmacy

        # create or update stock
        product = validated_data["product"]

        stock, created = Stock.objects.get_or_create(
            pharmacy=pharmacy,
            product=product,
            defaults=validated_data
        )

        if not created:
            stock.quantity += validated_data.get("quantity", 0)
            stock.batch_number = validated_data.get("batch_number", stock.batch_number)
            stock.expiry_date = validated_data.get("expiry_date", stock.expiry_date)
            stock.save()

        return stock

# =====================================
# STOCK
# =====================================
class StockSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.ReadOnlyField(source="pharmacy.name")
    product_name = serializers.ReadOnlyField(source="product.name")
    category = serializers.ReadOnlyField(source="product.category")
    unit = serializers.ReadOnlyField(source="product.unit")

    class Meta:
        model = Stock
        fields = "__all__"
        read_only_fields = ("pharmacy",)
        validators = []

    def validate(self, attrs):
        print("\n========== STOCK VALIDATION ==========")
        print("Incoming Data :", attrs)

        if "product" not in attrs:
            raise serializers.ValidationError({
                "product": "Product is required."
            })

        if "quantity" not in attrs:
            raise serializers.ValidationError({
                "quantity": "Quantity is required."
            })

        if attrs["quantity"] <= 0:
            raise serializers.ValidationError({
                "quantity": "Quantity must be greater than zero."
            })

        print("Validation Passed")
        print("======================================\n")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        if request is None:
            raise serializers.ValidationError({
                "request": "Request context missing."
            })

        user = request.user

        print("\n========== CREATE STOCK ==========")
        print("User :", user.username)

        profile = getattr(user, "profile", None)

        if profile is None:
            raise serializers.ValidationError({
                "profile": "User profile not found."
            })

        print("Role :", profile.role)

        if profile.role != "staff":
            raise serializers.ValidationError({
                "role": "Only staff can add stock."
            })

        staff = PharmacyStaff.objects.filter(user=user).first()

        print("Staff :", staff)

        if staff is None:
            raise serializers.ValidationError({
                "staff": "This user is not linked to any pharmacy."
            })

        pharmacy = staff.pharmacy

        print("Pharmacy :", pharmacy)
        print("Validated Data :", validated_data)

        product = validated_data["product"]
        quantity = validated_data["quantity"]

        stock, created = Stock.objects.get_or_create(
            pharmacy=pharmacy,
            product=product,
            defaults={
                "quantity": quantity,
                "batch_number": validated_data.get("batch_number"),
                "expiry_date": validated_data.get("expiry_date"),
            },
        )

        if created:
            print("New stock created.")
        else:
            print("Existing stock found. Updating quantity.")
            stock.quantity += quantity

            if validated_data.get("batch_number"):
                stock.batch_number = validated_data["batch_number"]

            if validated_data.get("expiry_date"):
                stock.expiry_date = validated_data["expiry_date"]

            stock.save()

        print("Saved Stock :", stock.id)
        print("===================================\n")

        return stock
# =====================================
# RESERVATION
# =====================================
class ReservationSerializer(serializers.ModelSerializer):

    patient_name = serializers.ReadOnlyField(source="user.username")
    pharmacy_name = serializers.ReadOnlyField(source="pharmacy.name")
    product_name = serializers.ReadOnlyField(source="product.name")
    category = serializers.ReadOnlyField(source="product.category")
    unit = serializers.ReadOnlyField(source="product.unit")

    class Meta:
        model = Reservation
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            profile = get_profile(request.user)

            if not profile or profile.role != "patient":
                raise serializers.ValidationError("Only patients can make reservations")

            validated_data["user"] = request.user

        return Reservation.objects.create(**validated_data)


# =====================================
# JWT LOGIN (STAFF ONLY)
# =====================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        profile = get_profile(user)

        if not profile:
            raise serializers.ValidationError("Profile not found")

        if profile.role != "staff":
            raise serializers.ValidationError("Only staff can login here")

        data["username"] = user.username
        data["role"] = profile.role

        return data


# =====================================
# PATIENT LOGIN (OPTIONAL)
# =====================================
class PatientTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        profile = get_profile(user)

        if not profile:
            raise serializers.ValidationError("Profile not found")

        if profile.role != "patient":
            raise serializers.ValidationError("Only patient can login here")

        data["username"] = user.username
        data["role"] = profile.role

        return data