from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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

    password = serializers.CharField(
        write_only=True,
        required=False
    )


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


        # Default registration = patient
        UserProfile.objects.create(
            user=user,
            role="patient"
        )


        return user




# =====================================
# USER PROFILE
# =====================================

class UserProfileSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
        allow_blank=False
    )


    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "username",
            "email",
            "role",
            "phone",
            "address",
            "gender",
            "date_of_birth",
        ]
        read_only_fields = ["user", "username", "role"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")

        if email is not None:
            instance.user.email = email
            instance.user.save(update_fields=["email"])

        return super().update(instance, validated_data)





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

    pharmacy_name = serializers.ReadOnlyField(
        source="pharmacy.name"
    )


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
# STOCK
# =====================================

class StockSerializer(serializers.ModelSerializer):


    pharmacy_name = serializers.ReadOnlyField(
        source="pharmacy.name"
    )


    pharmacy_location = serializers.ReadOnlyField(
        source="pharmacy.location_name"
    )


    latitude = serializers.ReadOnlyField(
        source="pharmacy.latitude"
    )


    longitude = serializers.ReadOnlyField(
        source="pharmacy.longitude"
    )



    product_name = serializers.ReadOnlyField(
        source="product.name"
    )


    prescription = serializers.ReadOnlyField(
        source="product.requires_prescription"
    )


    category = serializers.ReadOnlyField(
        source="product.category"
    )


    unit = serializers.ReadOnlyField(
        source="product.unit"
    )



    class Meta:

        model = Stock


        fields = [

            "id",

            "product",
            "product_name",

            "pharmacy",
            "pharmacy_name",

            "pharmacy_location",

            "latitude",
            "longitude",

            "prescription",

            "category",
            "unit",

            "quantity",

            "batch_number",

            "expiry_date",

        ]


        read_only_fields = [

            "pharmacy"

        ]




    # ============================
    # VALIDATION
    # ============================

    def validate(self, attrs):


        if "product" not in attrs:

            raise serializers.ValidationError(

                {
                    "product":
                    "Product is required"

                }

            )



        if "quantity" not in attrs:

            raise serializers.ValidationError(

                {
                    "quantity":
                    "Quantity is required"

                }

            )



        if attrs["quantity"] <= 0:


            raise serializers.ValidationError(

                {
                    "quantity":
                    "Quantity must be greater than zero"

                }

            )



        return attrs





    # ============================
    # CREATE STOCK
    # ============================

    def create(self, validated_data):


        request = self.context.get("request")



        if request is None:

            raise serializers.ValidationError(

                "Request context missing"

            )



        user = request.user



        profile = get_profile(user)



        if not profile:

            raise serializers.ValidationError(

                "Profile not found"

            )




        if profile.role != "staff":

            raise serializers.ValidationError(

                "Only staff can manage stock"

            )





        staff = PharmacyStaff.objects.filter(

            user=user

        ).first()




        if not staff:


            raise serializers.ValidationError(

                "Staff not linked to pharmacy"

            )





        pharmacy = staff.pharmacy




        product = validated_data["product"]


        quantity = validated_data["quantity"]





        stock, created = Stock.objects.get_or_create(


            pharmacy=pharmacy,


            product=product,



            defaults={


                "quantity": quantity,


                "batch_number":

                validated_data.get(
                    "batch_number"
                ),



                "expiry_date":

                validated_data.get(
                    "expiry_date"
                ),


            }


        )





        if not created:



            stock.quantity += quantity




            if validated_data.get("batch_number"):


                stock.batch_number = (

                    validated_data["batch_number"]

                )




            if validated_data.get("expiry_date"):


                stock.expiry_date = (

                    validated_data["expiry_date"]

                )




            stock.save()




        return stock

class ReservationSerializer(serializers.ModelSerializer):

    patient_name = serializers.ReadOnlyField(source="user.username")
    pharmacy_name = serializers.ReadOnlyField(source="pharmacy.name")
    product_name = serializers.ReadOnlyField(source="product.name")
    category = serializers.ReadOnlyField(source="product.category")
    unit = serializers.ReadOnlyField(source="product.unit")

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = (
            "user",
            "reservation_date",
            "status",
            "processed_by",
        )

    def create(self, validated_data):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            profile = get_profile(request.user)

            if not profile or profile.role != "patient":
                raise serializers.ValidationError(
                    "Only patients can make reservations."
                )

            validated_data["user"] = request.user

        return Reservation.objects.create(**validated_data)

# =====================================
# JWT LOGIN
# STAFF + PATIENT
# =====================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):


    def validate(self, attrs):

        data = super().validate(attrs)


        user = self.user


        profile = get_profile(user)



        if not profile:

            raise serializers.ValidationError(
                {
                    "error":
                    "User profile not found"
                }
            )



        if profile.role not in [
            "staff",
            "patient"
        ]:


            raise serializers.ValidationError(
                {
                    "error":
                    "User role not allowed"
                }
            )



        data["user_id"] = user.id

        data["username"] = user.username

        data["email"] = user.email

        data["role"] = profile.role



        return data